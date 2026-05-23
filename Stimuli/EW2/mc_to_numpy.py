import numpy as np
from PIL import Image
import random

# -----------------------------
# Helper Functions
# -----------------------------
def load_montage(image_path, frame_width, frame_height, color_sequence='BGR'):
    """
    Load a montage image and split it into individual frames.
    The coordinate system is defined such that (0,0) is at the bottom-left.

    Args:
        image_path: Path to the montage image file.
        frame_width: Width of each frame in pixels.
        frame_height: Height of each frame in pixels.
        color_sequence: 'BGR' or 'RGB' indicating the color channel order.

    Returns:
        frames: NumPy array of shape (num_frames, height, width, 3)
    """
    # Load image and convert to RGB
    img = Image.open(image_path).convert('RGB')
    if color_sequence == 'BGR':
        r, g, b = img.split()
        img = Image.merge("RGB", (b, g, r))
    elif color_sequence != 'RGB':
        raise ValueError("color_sequence must be 'BGR' or 'RGB'")
    img_np = np.array(img)

    total_height, total_width, _ = img_np.shape
    cols = total_width // frame_width
    rows = total_height // frame_height
    num_frames = rows * cols

    frames = []
    for row in range(rows):
        # Flip row index to make 0,0 at the bottom-left
        flipped_row = rows - 1 - row
        for col in range(cols):
            x_start = col * frame_width
            y_start = flipped_row * frame_height
            frame = img_np[y_start:y_start + frame_height, x_start:x_start + frame_width, :]
            frames.append(frame)

    frames = np.array(frames, dtype=np.uint8)
    assert num_frames == len(frames)

    return frames


def build_movie(p, sequence_column=None, color_sequence='BGR'):
    """
    Build the full stimulus sequence following the logic of the original QDSpy script.

    Args:
        p: Dictionary with parameters.
        sequence_column: If None, a random column will be chosen.
        color_sequence: 'BGR' or 'RGB' indicating the color channel order.

    Returns:
        movie: NumPy array of shape (height, width, time, 3)
        used_column: The actual random sequence column that was used.
    """
    # Load random sequence file
    indices = np.loadtxt(p["IndexName"])
    num_columns = indices.shape[1]

    # Choose which random sequence column to use
    if sequence_column is None:
        sequence_column = random.randint(0, num_columns - 1)

    height, width = p["frame_height"], p["frame_width"]

    # Load montages
    test_frames = load_montage(p["movName_Test"], width, height, color_sequence=color_sequence)
    print('Test frames loaded:', test_frames.shape)
    train_frames = load_montage(p["movName_Train"], width, height, color_sequence=color_sequence)
    print('Train frames loaded:', train_frames.shape)

    # Frame counts
    nFr_Test = test_frames.shape[0]
    nFr_Train = train_frames.shape[0]
    nSeqs_Train = int(nFr_Train / (p["durSnippet_s"] * p["FrameRateMovie"]))
    nFr_Sequ = int(p["durSnippet_s"] * p["FrameRateMovie"])

    print(f"Test frames: {nFr_Test}, Train frames: {nFr_Train}"
          f"Train sequences: {nSeqs_Train}, Frames per sequence: {nFr_Sequ}")

    # Total sequence length (upper bound estimate)
    total_frames = 3 * nFr_Test + nFr_Train

    # Initialize sequence
    movie = np.zeros((total_frames, height, width, 3), dtype=np.uint8)
    t = 0

    def insert_test_block():
        nonlocal t
        movie[t:t+nFr_Test] = test_frames
        t += nFr_Test

    # -----------------------------
    # Test Set #1
    # -----------------------------
    insert_test_block()

    # -----------------------------
    # First half of training set
    # -----------------------------
    for iF in range(int(nSeqs_Train / 2)):
        FrameStart = int(indices[iF][sequence_column]) * nFr_Sequ
        FrameEnd = (int(indices[iF][sequence_column]) + 1) * nFr_Sequ - 1
        movie[t:t + nFr_Sequ] = train_frames[FrameStart:FrameEnd + 1]
        t += nFr_Sequ

    # -----------------------------
    # Test Set #2
    # -----------------------------
    insert_test_block()

    # -----------------------------
    # Second half of training set
    # -----------------------------
    for iF in range(int(nSeqs_Train / 2)):
        a = iF + int(nSeqs_Train / 2)
        FrameStart = int(indices[a][sequence_column]) * nFr_Sequ
        FrameEnd = (int(indices[a][sequence_column]) + 1) * nFr_Sequ - 1
        movie[t:t + nFr_Sequ] = train_frames[FrameStart:FrameEnd + 1]
        t += nFr_Sequ

    # -----------------------------
    # Test Set #3
    # -----------------------------
    insert_test_block()

    # Trim excess sequence
    movie = movie[:, :, :t, :]

    return movie, sequence_column


# -----------------------------
# Main Entry Point
# -----------------------------
def main(sequence_column=None, color_sequence='BGR'):
    """
    Main function to generate the stimulus sequence.
    Set sequence_column to force a specific column, or leave as None for random.
    """
    # Parameter dictionary
    p = {
        "durSnippet_s": 5.0,             # each snippet is 5 seconds
        "FrameRateMovie": 30.0,          # frames per second
        "movName_Test": "test_images_rand_right.jpg",
        "movName_Train": "train_images_right.jpg",
        "IndexName": "RandomSequences.txt",
        "frame_width": 56,                # from movparams
        "frame_height": 56,
    }

    sequence, used_column = build_movie(p, sequence_column, color_sequence=color_sequence)
    np.save(f"mc_arrays/MC{used_column}.npy", sequence)


if __name__ == "__main__":
    #main(sequence_column=0)

    for i in range(20):
        main(sequence_column=i)
