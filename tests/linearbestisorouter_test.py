# -*- coding: utf-8 -*-
# Copyright (C) 2017-2025 Davide Gessa
# Copyright (C) 2021 Enrico Ferreguti
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# For detail about GNU see <http://www.gnu.org/licenses/>.
import datetime

# import json
import math
import os
import unittest

import weatherrouting
from weatherrouting.routers.linearbestisorouter import LinearBestIsoRouter

from .mock_grib import MockGrib
from .mock_point_validity import MockPointValidity

polar_bavaria38 = weatherrouting.Polar(
    os.path.join(os.path.dirname(__file__), "data/bavaria38.pol")
)


def heading(y, x):
    a = math.degrees(math.atan2(y, x))
    if a < 0:
        a = 360 + a
    return (90 - a + 360) % 360


# class TestRouting_straigth_upwind(unittest.TestCase):
#     def test_step(self):
#         base_step = [
#             [1, 0],
#             [1, 1],
#             [0, 1],
#             [-1, 1],
#             [-1, 0],
#             [-1, -1],
#             [0, -1],
#             [1, -1],
#         ]
#         base_start = [34, 17]
#         base_gjs = {}

#         for s in base_step:
#             base_end = [base_start[0] + s[0], base_start[1] + s[1]]
#             head = heading(*s)
#             print("TEST UPWIND TWD", head, "step", s)
#             pvmodel = MockPointValidity([base_start, base_end])
#             routing_obj = weatherrouting.Routing(
#                 LinearBestIsoRouter,
#                 polar_bavaria38,
#                 [base_start, base_end],
#                 MockGrib(10, head, 0),
#                 datetime.datetime.fromisoformat("2021-04-02T12:00:00"),
#                 lineValidity=pvmodel.line_validity,
#             )
#             res = None
#             i = 0

#             while not routing_obj.end:
#                 res = routing_obj.step()
#                 i += 1

#             path_to_end = res.path
#             if not base_gjs:
#                 base_gjs = weatherrouting.utils.pathAsGeojson(path_to_end)
#             else:
#                 base_gjs["features"] += weatherrouting.utils.pathAsGeojson(path_to_end)[
#                     "features"
#                 ]
#             gjs = json.dumps(base_gjs)

#         print(gjs)


class TestRouting_lowWind_noIsland(unittest.TestCase):
    def setUp(self):
        grib = MockGrib(2, 180, 0.1)
        self.track = [(5, 38), (5.2, 38.2)]
        island_route = MockPointValidity(self.track)
        self.routing_obj = weatherrouting.Routing(
            LinearBestIsoRouter,
            polar_bavaria38,
            self.track,
            grib,
            datetime.datetime.fromisoformat("2021-04-02T12:00:00"),
            pointValidity=island_route.point_validity,
        )

    def test_step(self):
        res = None
        i = 0

        while not self.routing_obj.end:
            res = self.routing_obj.step()
            i += 1

        self.assertEqual(i, 7)
        self.assertEqual(not res.path, False)

        path_to_end = res.path
        self.assertEqual(
            res.time, datetime.datetime.fromisoformat("2021-04-02 18:00:00")
        )

        gj = weatherrouting.utils.pathAsGeojson(path_to_end)

        self.assertEqual(len(gj["features"]), 8)
        self.assertEqual(
            gj["features"][-1]["properties"]["end-timestamp"], "2021-04-02 18:00:00"
        )


class TestRouting_lowWind_mockIsland_5(unittest.TestCase):
    def setUp(self):
        grib = MockGrib(2, 180, 0.1)
        self.track = [(5, 38), (5.2, 38.2)]
        island_route = MockPointValidity(self.track, factor=5)
        self.routing_obj = weatherrouting.Routing(
            LinearBestIsoRouter,
            polar_bavaria38,
            self.track,
            grib,
            datetime.datetime.fromisoformat("2021-04-02T12:00:00"),
            pointValidity=island_route.point_validity,
        )

    def test_step(self):
        res = None
        i = 0

        while not self.routing_obj.end:
            res = self.routing_obj.step()
            i += 1

        self.assertEqual(i, 7)
        self.assertEqual(not res.path, False)


class checkRoute_mediumWind_mockIsland_8(unittest.TestCase):
    def setUp(self):
        grib = MockGrib(5, 45, 0.5)
        self.track = [(5, 38), (4.6, 37.6)]
        island_route = MockPointValidity(self.track, factor=8)
        self.routing_obj = weatherrouting.Routing(
            LinearBestIsoRouter,
            polar_bavaria38,
            self.track,
            grib,
            datetime.datetime.fromisoformat("2021-04-02T12:00:00"),
            lineValidity=island_route.line_validity,
        )

    def test_step(self):
        res = None
        i = 0

        while not self.routing_obj.end:
            res = self.routing_obj.step()
            i += 1

        self.assertEqual(i, 7)
        self.assertEqual(not res.path, False)


class checkRoute_highWind_mockIsland_3(unittest.TestCase):
    def setUp(self):
        grib = MockGrib(10, 270, 0.5)
        self.track = [(5, 38), (5.5, 38.5)]
        island_route = MockPointValidity(self.track, factor=3)
        self.routing_obj = weatherrouting.Routing(
            LinearBestIsoRouter,
            polar_bavaria38,
            self.track,
            grib,
            datetime.datetime.fromisoformat("2021-04-02T12:00:00"),
            lineValidity=island_route.line_validity,
        )

    def test_step(self):
        res = None
        i = 0

        while not self.routing_obj.end:
            res = self.routing_obj.step()
            i += 1

        self.assertEqual(i, 7)
        self.assertEqual(not res.path, False)


class checkRoute_out_of_scope(unittest.TestCase):
    def setUp(self):
        grib = MockGrib(
            10,
            270,
            0.5,
            out_of_scope=datetime.datetime.fromisoformat("2021-04-02T15:00:00"),
        )
        self.track = [(5, 38), (5.5, 38.5)]
        island_route = MockPointValidity(self.track, factor=3)
        self.routing_obj = weatherrouting.Routing(
            LinearBestIsoRouter,
            polar_bavaria38,
            self.track,
            grib,
            datetime.datetime.fromisoformat("2021-04-02T12:00:00"),
            lineValidity=island_route.line_validity,
        )

    def test_step(self):
        res = None
        i = 0

        while not self.routing_obj.end:
            res = self.routing_obj.step()
            i += 1

        self.assertEqual(i, 4)
        self.assertEqual(not res.path, False)


class checkRoute_multipoint(unittest.TestCase):
    def setUp(self):
        grib = MockGrib(10, 270, 0.5)
        self.track = [(5, 38), (5.3, 38.3), (5.6, 38.6)]
        # island_route = MockPointValidity(self.track, factor=3)
        self.routing_obj = weatherrouting.Routing(
            LinearBestIsoRouter,
            polar_bavaria38,
            self.track,
            grib,
            datetime.datetime.fromisoformat("2021-04-02T12:00:00"),
        )

    def test_step(self):
        res = None
        i = 0

        while not self.routing_obj.end:
            res = self.routing_obj.step()
            i += 1

        self.assertEqual(i, 6)
        self.assertEqual(not res.path, False)


class TestRouting_custom_step(unittest.TestCase):
    def setUp(self):
        grib = MockGrib(2, 180, 0.1)
        self.track = [(5, 38), (5.2, 38.2)]
        island_route = MockPointValidity(self.track, factor=5)
        self.routing_obj = weatherrouting.Routing(
            LinearBestIsoRouter,
            polar_bavaria38,
            self.track,
            grib,
            datetime.datetime.fromisoformat("2021-04-02T12:00:00"),
            pointValidity=island_route.point_validity,
        )

    def test_step(self):
        res = None
        i = 0

        while not self.routing_obj.end:
            res = self.routing_obj.step(timedelta=0.5)
            i += 1

        self.assertEqual(i, 12)
        self.assertEqual(not res.path, False)
