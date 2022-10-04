"""
Model exported as python.
Name : updated_clusterboundary
Group : 
With QGIS : 32403
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterFeatureSink
from qgis.core import QgsCoordinateReferenceSystem
import processing


class Updated_clusterboundary(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('demandpoints', 'demandpoints', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('landboundary', 'landboundary', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('referencepoints', 'referencepoints', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('streetcenterlines', 'streetcenterlines', types=[QgsProcessing.TypeVectorLine], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('topographiclines', 'topographiclines', types=[QgsProcessing.TypeVectorLine], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Cluster_bndry', 'cluster_bndry', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Mdu', 'mdu', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(31, model_feedback)
        results = {}
        outputs = {}

        # Extract by expression_mdu
        alg_params = {
            'EXPRESSION': ' "loc_desc"  =  \'MDU\'',
            'INPUT': parameters['demandpoints'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByExpression_mdu'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Points to path
        alg_params = {
            'CLOSE_PATH': True,
            'GROUP_EXPRESSION': 'struct_id',
            'INPUT': parameters['referencepoints'],
            'NATURAL_SORT': False,
            'ORDER_EXPRESSION': 'struct_id',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['PointsToPath'] = processing.run('native:pointstopath', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Buffer
        alg_params = {
            'DISSOLVE': False,
            'DISTANCE': 1,
            'END_CAP_STYLE': 0,  # Round
            'INPUT': outputs['PointsToPath']['OUTPUT'],
            'JOIN_STYLE': 0,  # Round
            'MITER_LIMIT': 1.2,
            'SEGMENTS': 5,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Buffer'] = processing.run('native:buffer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Snap geometries to layer_dp
        alg_params = {
            'BEHAVIOR': 3,  # Prefer closest point, don't insert new vertices
            'INPUT': parameters['demandpoints'],
            'REFERENCE_LAYER': parameters['landboundary'],
            'TOLERANCE': 1,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['SnapGeometriesToLayer_dp'] = processing.run('native:snapgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # Points along geometry
        alg_params = {
            'DISTANCE': 0.5,
            'END_OFFSET': 0,
            'INPUT': parameters['streetcenterlines'],
            'START_OFFSET': 0,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['PointsAlongGeometry'] = processing.run('native:pointsalonglines', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # Extract by location_landbndry
        alg_params = {
            'INPUT': parameters['landboundary'],
            'INTERSECT': outputs['SnapGeometriesToLayer_dp']['OUTPUT'],
            'PREDICATE': [0],  # intersect
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByLocation_landbndry'] = processing.run('native:extractbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # Distance to nearest hub (line to hub)
        alg_params = {
            'FIELD': 'include',
            'HUBS': outputs['PointsAlongGeometry']['OUTPUT'],
            'INPUT': parameters['demandpoints'],
            'UNIT': 0,  # Meters
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DistanceToNearestHubLineToHub'] = processing.run('qgis:distancetonearesthublinetohub', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}

        # Multipart to singleparts
        alg_params = {
            'INPUT': outputs['Buffer']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['MultipartToSingleparts'] = processing.run('native:multiparttosingleparts', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(8)
        if feedback.isCanceled():
            return {}

        # Snap geometries to layer
        alg_params = {
            'BEHAVIOR': 1,  # Prefer closest point, insert extra vertices where required
            'INPUT': outputs['DistanceToNearestHubLineToHub']['OUTPUT'],
            'REFERENCE_LAYER': parameters['streetcenterlines'],
            'TOLERANCE': 1,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['SnapGeometriesToLayer'] = processing.run('native:snapgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(9)
        if feedback.isCanceled():
            return {}

        # Merge vector layers_wholeland
        alg_params = {
            'CRS': QgsCoordinateReferenceSystem('EPSG:27700'),
            'LAYERS': [parameters['streetcenterlines'],parameters['topographiclines'],outputs['SnapGeometriesToLayer']['OUTPUT']],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['MergeVectorLayers_wholeland'] = processing.run('native:mergevectorlayers', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(10)
        if feedback.isCanceled():
            return {}

        # Convex hull
        alg_params = {
            'INPUT': outputs['MultipartToSingleparts']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ConvexHull'] = processing.run('native:convexhull', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(11)
        if feedback.isCanceled():
            return {}

        # Polygons to lines
        alg_params = {
            'INPUT': outputs['ConvexHull']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['PolygonsToLines'] = processing.run('native:polygonstolines', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(12)
        if feedback.isCanceled():
            return {}

        # Polygonize_wholeland
        alg_params = {
            'INPUT': outputs['MergeVectorLayers_wholeland']['OUTPUT'],
            'KEEP_FIELDS': False,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Polygonize_wholeland'] = processing.run('native:polygonize', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(13)
        if feedback.isCanceled():
            return {}

        # Split with lines
        alg_params = {
            'INPUT': outputs['ConvexHull']['OUTPUT'],
            'LINES': outputs['PolygonsToLines']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['SplitWithLines'] = processing.run('native:splitwithlines', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(14)
        if feedback.isCanceled():
            return {}

        # Difference_missinglandnstreet
        alg_params = {
            'INPUT': outputs['Polygonize_wholeland']['OUTPUT'],
            'OVERLAY': outputs['ExtractByLocation_landbndry']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Difference_missinglandnstreet'] = processing.run('native:difference', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(15)
        if feedback.isCanceled():
            return {}

        # Extract by location
        alg_params = {
            'INPUT': outputs['Polygonize_wholeland']['OUTPUT'],
            'INTERSECT': outputs['ExtractByExpression_mdu']['OUTPUT'],
            'PREDICATE': [0],  # intersect
            'OUTPUT': parameters['Mdu']
        }
        outputs['ExtractByLocation'] = processing.run('native:extractbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Mdu'] = outputs['ExtractByLocation']['OUTPUT']

        feedback.setCurrentStep(16)
        if feedback.isCanceled():
            return {}

        # Merge vector layers_lns
        alg_params = {
            'CRS': QgsCoordinateReferenceSystem('EPSG:27700'),
            'LAYERS': [outputs['ExtractByLocation_landbndry']['OUTPUT'],outputs['Difference_missinglandnstreet']['OUTPUT']],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['MergeVectorLayers_lns'] = processing.run('native:mergevectorlayers', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(17)
        if feedback.isCanceled():
            return {}

        # Delete duplicate geometrie2
        alg_params = {
            'INPUT': outputs['SplitWithLines']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DeleteDuplicateGeometrie2'] = processing.run('native:deleteduplicategeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(18)
        if feedback.isCanceled():
            return {}

        # Join attributes by location_mpland
        alg_params = {
            'DISCARD_NONMATCHING': True,
            'INPUT': outputs['MergeVectorLayers_lns']['OUTPUT'],
            'JOIN': parameters['referencepoints'],
            'JOIN_FIELDS': ['struct_id'],
            'METHOD': 2,  # Take attributes of the feature with largest overlap only (one-to-one)
            'PREDICATE': [0],  # intersect
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByLocation_mpland'] = processing.run('native:joinattributesbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(19)
        if feedback.isCanceled():
            return {}

        # Difference
        alg_params = {
            'INPUT': outputs['MergeVectorLayers_lns']['OUTPUT'],
            'OVERLAY': outputs['JoinAttributesByLocation_mpland']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Difference'] = processing.run('native:difference', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(20)
        if feedback.isCanceled():
            return {}

        # Drop field(s)
        alg_params = {
            'COLUMN': ['struct_id'],
            'INPUT': outputs['DeleteDuplicateGeometrie2']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DropFields'] = processing.run('native:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(21)
        if feedback.isCanceled():
            return {}

        # Join attributes by location_convexhull
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'INPUT': outputs['DropFields']['OUTPUT'],
            'JOIN': parameters['referencepoints'],
            'JOIN_FIELDS': ['struct_id'],
            'METHOD': 2,  # Take attributes of the feature with largest overlap only (one-to-one)
            'PREDICATE': [0],  # intersect
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByLocation_convexhull'] = processing.run('native:joinattributesbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(22)
        if feedback.isCanceled():
            return {}

        # Join attributes by nearest_diff
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELDS_TO_COPY': ['struct_id'],
            'INPUT': outputs['Difference']['OUTPUT'],
            'INPUT_2': outputs['JoinAttributesByLocation_convexhull']['OUTPUT'],
            'MAX_DISTANCE': 5,
            'NEIGHBORS': 1,
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByNearest_diff'] = processing.run('native:joinbynearest', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(23)
        if feedback.isCanceled():
            return {}

        # Extract by expression
        alg_params = {
            'EXPRESSION': ' "struct_id"  is not null',
            'INPUT': outputs['JoinAttributesByNearest_diff']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByExpression'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(24)
        if feedback.isCanceled():
            return {}

        # Merge vector layers
        alg_params = {
            'CRS': QgsCoordinateReferenceSystem('EPSG:27700'),
            'LAYERS': [outputs['JoinAttributesByLocation_mpland']['OUTPUT'],outputs['ExtractByExpression']['OUTPUT']],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['MergeVectorLayers'] = processing.run('native:mergevectorlayers', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(25)
        if feedback.isCanceled():
            return {}

        # Dissolve
        alg_params = {
            'FIELD': ['struct_id'],
            'INPUT': outputs['MergeVectorLayers']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Dissolve'] = processing.run('native:dissolve', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(26)
        if feedback.isCanceled():
            return {}

        # Delete holes
        alg_params = {
            'INPUT': outputs['Dissolve']['OUTPUT'],
            'MIN_AREA': 50,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DeleteHoles'] = processing.run('native:deleteholes', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(27)
        if feedback.isCanceled():
            return {}

        # Polygons to lines_fnl
        alg_params = {
            'INPUT': outputs['DeleteHoles']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['PolygonsToLines_fnl'] = processing.run('native:polygonstolines', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(28)
        if feedback.isCanceled():
            return {}

        # Polygonize
        alg_params = {
            'INPUT': outputs['PolygonsToLines_fnl']['OUTPUT'],
            'KEEP_FIELDS': False,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Polygonize'] = processing.run('native:polygonize', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(29)
        if feedback.isCanceled():
            return {}

        # Join attributes by nearest
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELDS_TO_COPY': ['struct_id'],
            'INPUT': outputs['Polygonize']['OUTPUT'],
            'INPUT_2': parameters['referencepoints'],
            'MAX_DISTANCE': None,
            'NEIGHBORS': 1,
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByNearest'] = processing.run('native:joinbynearest', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(30)
        if feedback.isCanceled():
            return {}

        # Dissolve
        alg_params = {
            'FIELD': ['struct_id'],
            'INPUT': outputs['JoinAttributesByNearest']['OUTPUT'],
            'OUTPUT': parameters['Cluster_bndry']
        }
        outputs['Dissolve'] = processing.run('native:dissolve', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Cluster_bndry'] = outputs['Dissolve']['OUTPUT']
        return results

    def name(self):
        return 'updated_clusterboundary'

    def displayName(self):
        return 'updated_clusterboundary'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return Updated_clusterboundary()
