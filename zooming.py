def zoom_image(frame, zoom_factor=2.0):
    height, width = frame.shape[:2]
    center_x, center_y = width // 2, height // 2

    new_width = int(width / zoom_factor)
    new_height = int(height / zoom_factor)

    x1 = max(center_x - new_width // 2, 0)
    y1 = max(center_y - new_height // 2, 0)
    x2 = min(center_x + new_width // 2, width)
    y2 = min(center_y + new_height // 2, height)

    zoomed_frame = frame[y1:y2, x1:x2]
    return cv2.resize(zoomed_frame, (width, height))

# In your `update_frame` method:
zoom_factor = 2.0  # Adjust as needed
frame = zoom_image(frame, zoom_factor)
