def divide_window(frame, rows, cols):
    height, width = frame.shape[:2]
    row_height = height // rows
    col_width = width // cols
    grid_frames = []
    
    for i in range(rows):
        for j in range(cols):
            start_x = j * col_width
            start_y = i * row_height
            end_x = (j + 1) * col_width
            end_y = (i + 1) * row_height
            grid_frames.append(frame[start_y:end_y, start_x:end_x])
    
    return grid_frames

# In your `update_frame` method:
rows, cols = 1, 7  # Example for 1x7 division
grid_frames = divide_window(frame, rows, cols)

# To display each grid frame:
for idx, grid_frame in enumerate(grid_frames):
    # Handle the display of each grid_frame here
    pass
