"""Reject unsafe painted crop boundaries before any batch output is written."""
def validate_visible_boundaries(image, rects, threshold=16):
    width, height = image.size
    for index, rect in enumerate(rects):
        if len(rect) != 4 or not all(isinstance(value, int) for value in rect):
            raise ValueError(f'Invalid crop rectangle {index}')
        left, top, right, bottom = rect
        if not (0 <= left < right <= width and 0 <= top < bottom <= height):
            raise ValueError(f'Out-of-bounds crop {index}')
        alpha = image.crop(rect).getchannel('A')
        w, h = alpha.size
        edges = ((0, 0, 1, h), (w - 1, 0, w, h), (0, 0, w, 1), (0, h - 1, w, h))
        if any(any(value >= threshold for value in alpha.crop(edge).tobytes()) for edge in edges):
            raise ValueError(f'Visible pixels cross crop {index}; review actual alpha before export')
