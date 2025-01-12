# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Calculate Geometry
                                 A QGIS plugin
 Calculate area, length
                             -------------------
        begin                : 2018-02-06
        copyright            : (C) 2018 by Tarot Osuji
        email                : tarot@sdf.org
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from qgis.core import QgsUnitTypes


distance_units = (QgsUnitTypes.DistanceMeters,
                  QgsUnitTypes.DistanceKilometers,
                  QgsUnitTypes.DistanceFeet,
                  QgsUnitTypes.DistanceYards,
                  QgsUnitTypes.DistanceMiles,
                  QgsUnitTypes.DistanceNauticalMiles,
                  QgsUnitTypes.DistanceCentimeters,
                  QgsUnitTypes.DistanceMillimeters,
                  QgsUnitTypes.DistanceDegrees,
                  QgsUnitTypes.DistanceUnknownUnit)
area_units     = (QgsUnitTypes.AreaSquareMeters,
                  QgsUnitTypes.AreaSquareKilometers,
                  QgsUnitTypes.AreaSquareFeet,
                  QgsUnitTypes.AreaSquareYards,
                  QgsUnitTypes.AreaSquareMiles,
                  QgsUnitTypes.AreaHectares,
                  QgsUnitTypes.AreaAcres,
                  QgsUnitTypes.AreaSquareNauticalMiles,
                  QgsUnitTypes.AreaSquareCentimeters,
                  QgsUnitTypes.AreaSquareMillimeters,
                  QgsUnitTypes.AreaSquareDegrees,
                  QgsUnitTypes.AreaUnknownUnit)
