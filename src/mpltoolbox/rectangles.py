# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2022 Mpltoolbox contributors (https://github.com/mpltoolbox)

from .patches import Patches
from matplotlib.patches import Rectangle
from matplotlib.pyplot import Axes, Artist
from matplotlib.backend_bases import Event


def _vertices_from_rectangle(xy, width, height):
    return ([xy[0]] + [xy[0] + width] * 2 + [xy[0]], [xy[1]] * 2 + [xy[1] + height] * 2)


class Rectangles(Patches):
    """
    Add rectangles to the supplied axes.

    Controls:
      - Left-click and hold to make new rectangles
      - Right-click and hold to drag/move rectangle
      - Middle-click to delete rectangle

    :param ax: The Matplotlib axes to which the Lines tool will be attached.
    :param color: The rectangle colors. Can be a string (all lines will have the same
        color), a list of strings (one entry per rectangle), or a callable (this will be
        called every time a new rectangle is created and should return a color).
    :param autostart: Automatically activate the tool upon creation if `True`.
    :param on_create: Callback that fires when a rectangle is created.
    :param on_remove: Callback that fires when a rectangle is removed.
    :param on_drag_press: Callback that fires when a rectangle is right-clicked.
    :param on_drag_move: Callback that fires when a rectangle is dragged.
    :param on_drag_release: Callback that fires when a rectangle is released.
    """

    def __init__(self, ax: Axes, **kwargs):

        super().__init__(ax=ax, patch=Rectangle, **kwargs)

    def _resize_patch(self, event: Event):
        if event.inaxes != self._ax:
            return
        x, y = self.patches[-1].xy
        self.patches[-1].update({
            'width': event.xdata - x,
            'height': event.ydata - y,
        })
        self._draw()

    def _add_vertices(self):
        patch = self.patches[-1]
        vertices = _vertices_from_rectangle(xy=patch.xy,
                                            width=patch.get_width(),
                                            height=patch.get_height())

        line, = self._ax.plot(vertices[0],
                              vertices[1],
                              'o',
                              mec=patch.get_edgecolor(),
                              mfc='None',
                              picker=5.0)
        patch._vertices = line
        line._patch = patch

    def _move_vertex(self, event: Event, ind: int, line: Artist):
        if event.inaxes != self._ax:
            return
        x, y = line.get_data()
        x[ind] = event.xdata
        y[ind] = event.ydata
        opp = (ind + 2) % 4
        if ind == 0:
            width = x[opp] - x[ind]
            height = y[opp] - y[ind]
        elif ind == 1:
            width = x[ind] - x[opp]
            height = y[opp] - y[ind]
        elif ind == 2:
            width = x[ind] - x[opp]
            height = y[ind] - y[opp]
        elif ind == 3:
            width = x[opp] - x[ind]
            height = y[ind] - y[opp]
        xy = (min(x[ind], x[opp]) if width > 0 else max(x[ind], x[opp]),
              min(y[ind], y[opp]) if height > 0 else max(y[ind], y[opp]))
        line.set_data(_vertices_from_rectangle(xy=xy, width=width, height=height))
        line._patch.update({'xy': xy, 'width': width, 'height': height})
        self._draw()

    def _grab_patch(self, event: Event):
        super()._grab_patch(event)
        self._grab_artist_origin = self._grab_artist.xy

    def _update_artist_position(self, dx: float, dy: float):
        rect = self._grab_artist
        rect.xy = (self._grab_artist_origin[0] + dx, self._grab_artist_origin[1] + dy)
        rect._vertices.set_data(
            _vertices_from_rectangle(xy=rect.xy,
                                     width=rect.get_width(),
                                     height=rect.get_height()))
