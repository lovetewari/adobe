import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import distance
from scipy.interpolate import splprep, splev
import io
import svgwrite

# Function to read the CSV files from the uploaded file
def read_csv(uploaded_file):
    try:
        stringio = io.StringIO(uploaded_file.getvalue().decode("utf-8"))
        np_path_XYs = np.genfromtxt(stringio, delimiter=',')
        path_XYs = []
        for i in np.unique(np_path_XYs[:, 0]):
            npXYs = np_path_XYs[np_path_XYs[:, 0] == i][:, 1:]
            XYs = []
            for j in np.unique(npXYs[:, 0]):
                XY = npXYs[npXYs[:, 0] == j][:, 1:]
                XYs.append(XY)
            path_XYs.append(XYs)
        return path_XYs
    except Exception as e:
        st.error(f"Error reading CSV file: {e}")
        return None

# Function to plot the shapes
def plot(paths_XYs, title=''):
    fig, ax = plt.subplots(tight_layout=True, figsize=(8, 8))
    colours = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
    for i, XYs in enumerate(paths_XYs):
        c = colours[i % len(colours)]
        for XY in XYs:
            ax.plot(XY[:, 0], XY[:, 1], c=c, linewidth=2)
    ax.set_aspect('equal')
    plt.title(title)
    st.pyplot(fig)

# Function to detect and regularize shapes
def regularize_shapes(paths_XYs):
    regularized_paths_XYs = []
    for path in paths_XYs:
        for XY in path:
            # Check if the shape is a rectangle
            if len(XY) == 4 and np.allclose(np.abs(np.diff(np.arctan2(np.diff(XY[:, 1]), np.diff(XY[:, 0])))), np.pi / 2, atol=0.1):
                # Regularize rectangle
                centroid = np.mean(XY, axis=0)
                vectors = np.diff(np.vstack([XY, XY[0]]), axis=0)
                lengths = np.linalg.norm(vectors, axis=1)
                average_length = np.mean(lengths)
                angles = np.linspace(0, 2 * np.pi, 5)[:-1]
                regularized_XY = np.array([centroid + average_length / 2 * np.array([np.cos(angle), np.sin(angle)]) for angle in angles])
                regularized_paths_XYs.append([regularized_XY])

            # Check if the shape is a circle
            elif len(XY) > 2:
                centroid = np.mean(XY, axis=0)
                distances = distance.cdist([centroid], XY)[0]
                if np.std(distances) / np.mean(distances) < 0.1:
                    # Regularize circle
                    radius = np.mean(distances)
                    angles = np.linspace(0, 2 * np.pi, 100)
                    regularized_XY = np.array([[centroid[0] + radius * np.cos(angle), centroid[1] + radius * np.sin(angle)] for angle in angles])
                    regularized_paths_XYs.append([regularized_XY])
                else:
                    regularized_paths_XYs.append([XY])  # Keep original shape
            # Check if the shape is a regular polygon
            elif len(XY) >= 3:
                centroid = np.mean(XY, axis=0)
                distances = distance.cdist([centroid], XY)[0]
                if np.std(distances) / np.mean(distances) < 0.1:
                    # Regularize regular polygon
                    n = len(XY)
                    radius = np.mean(distances)
                    angles = np.linspace(0, 2 * np.pi, n, endpoint=False)
                    regularized_XY = np.array([[centroid[0] + radius * np.cos(angle), centroid[1] + radius * np.sin(angle)] for angle in angles])
                    regularized_paths_XYs.append([regularized_XY])
                else:
                    regularized_paths_XYs.append([XY])  # Keep original shape

            # Check if the shape is a star shape
            elif len(XY) >= 5 and len(XY) % 2 == 1:
                centroid = np.mean(XY, axis=0)
                distances = np.linalg.norm(XY - centroid, axis=1)
                alternating_distances = (np.std(distances[::2]) / np.mean(distances[::2]) < 0.1 and
                                         np.std(distances[1::2]) / np.mean(distances[1::2]) < 0.1)
                if alternating_distances:
                    # Regularize star shape
                    n = len(XY)
                    short_radius = np.mean(np.linalg.norm(XY[::2] - centroid, axis=1))
                    long_radius = np.mean(np.linalg.norm(XY[1::2] - centroid, axis=1))
                    angles = np.linspace(0, 2 * np.pi, n, endpoint=False)
                    regularized_XY = np.array([
                        [centroid[0] + (short_radius if i % 2 == 0 else long_radius) * np.cos(angle),
                         centroid[1] + (short_radius if i % 2 == 0 else long_radius) * np.sin(angle)]
                        for i, angle in enumerate(angles)
                    ])
                    regularized_paths_XYs.append([regularized_XY])
                else:
                    regularized_paths_XYs.append([XY])  # Keep original shape
            else:
                regularized_paths_XYs.append([XY])  # Keep original shape
    return regularized_paths_XYs

# Function to detect symmetry in shapes
def detect_symmetry(paths_XYs):
    def detect_reflection_symmetry(XY):
        n = len(XY)
        centroid = np.mean(XY, axis=0)
        distances = np.linalg.norm(XY - centroid, axis=1)
        angles = np.arctan2(XY[:, 1] - centroid[1], XY[:, 0] - centroid[0])
        for i in range(n):
            for j in range(i + 1, n):
                if np.isclose(distances[i], distances[j], atol=0.1) and np.isclose(np.abs(angles[i] - angles[j]), np.pi, atol=0.1):
                    return True, centroid
        return False, None

    symmetric_paths_XYs = []
    for XYs in paths_XYs:
        for XY in XYs:
            is_symmetric, centroid = detect_reflection_symmetry(XY)
            if is_symmetric:
                symmetric_paths_XYs.append([XY])
            else:
                symmetric_paths_XYs.append([XY])
    return symmetric_paths_XYs

# Function to complete gaps in shapes
def detect_and_complete_gaps(paths_XYs):
    def identify_gaps(XY):
        distances = np.linalg.norm(np.diff(XY, axis=0), axis=1)
        mean_distance = np.mean(distances)
        gap_indices = np.where(distances > 2 * mean_distance)[0]
        return gap_indices

    def complete_curve(XY, gap_indices):
        new_XY = []
        for i in range(len(XY) - 1):
            new_XY.append(XY[i])
            if i in gap_indices:
                tck, u = splprep([XY[:, 0], XY[:, 1]], s=0)
                u_new = np.linspace(u[i], u[i+1], num=5)
                x_new, y_new = splev(u_new, tck)
                new_points = np.column_stack([x_new, y_new])
                new_XY.extend(new_points[1:-1])
        new_XY.append(XY[-1])
        return np.array(new_XY)

    completed_paths_XYs = []
    for XYs in paths_XYs:
        for XY in XYs:
            gap_indices = identify_gaps(XY)
            if len(gap_indices) > 0:
                completed_XY = complete_curve(XY, gap_indices)
                completed_paths_XYs.append([completed_XY])
            else:
                completed_paths_XYs.append([XY])
    return completed_paths_XYs

# Combine all processing functions
def process_shapes(paths_XYs):
    paths_XYs = regularize_shapes(paths_XYs)
    symmetric_paths_XYs = detect_symmetry(paths_XYs)
    completed_paths_XYs = detect_and_complete_gaps(symmetric_paths_XYs)
    return completed_paths_XYs

# Save functions
def save_csv(paths_XYs, csv_path):
    with open(csv_path, 'w') as f:
        for i, XYs in enumerate(paths_XYs):
            for XY in XYs:
                for j, (x, y) in enumerate(XY):
                    f.write(f"{i},{j},{x},{y}\n")

def save_svg(paths_XYs, svg_path):
    dwg = svgwrite.Drawing(svg_path, profile='tiny')
    for i, XYs in enumerate(paths_XYs):
        for XY in XYs:
            valid_points = [(x, y) for x, y in XY if np.isfinite(x) and np.isfinite(y)]
            dwg.add(dwg.polygon(valid_points, stroke='black', fill='none'))
    dwg.save()

# Streamlit app
st.title("Shape Regularization and Symmetry Detection")

uploaded_file = st.file_uploader("Choose a CSV file", type="csv", key="unique_key")

if uploaded_file is not None:
    input_shapes = read_csv(uploaded_file)
    if input_shapes:
        st.subheader("Original Shapes")
        plot(input_shapes, title='Original Shapes')

        processed_shapes = process_shapes(input_shapes)
        
        st.subheader("Processed Shapes")
        plot(processed_shapes, title='Processed Shapes')
        
        if st.button("Download Processed Shapes as CSV"):
            save_csv(processed_shapes, 'processed_shapes.csv')
            st.download_button("Download CSV", data=open('processed_shapes.csv').read(), file_name='processed_shapes.csv', mime='text/csv')

        if st.button("Download Processed Shapes as SVG"):
            save_svg(processed_shapes, 'processed_shapes.svg')
            st.download_button("Download SVG", data=open('processed_shapes.svg').read(), file_name='processed_shapes.svg', mime='image/svg+xml')
