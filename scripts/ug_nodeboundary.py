"""
Model exported as python.
Name : ug_nodeboundary
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


class Ug_nodeboundary(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('clusters', 'clusters', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('demandpoints', 'demandpoints', defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('gaistdata', 'gaistdata', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('landbounadry', 'landbounadry', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('streetcenterline', 'streetcenterline', types=[QgsProcessing.TypeVectorLine], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('topographiclines', 'topographiclines', types=[QgsProcessing.TypeVectorLine], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Mdu', 'mdu', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Ug_boundary', 'ug_boundary', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(22, model_feedback)
        results = {}
        outputs = {}

        # Polygonize_topoarea
        alg_params = {
            'INPUT': parameters['topographiclines'],
            'KEEP_FIELDS': False,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Polygonize_topoarea'] = processing.run('native:polygonize', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Difference_missingtopo
        alg_params = {
            'INPUT': outputs['Polygonize_topoarea']['OUTPUT'],
            'OVERLAY': parameters['landbounadry'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Difference_missingtopo'] = processing.run('native:difference', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Polygons to lines
        alg_params = {
            'INPUT': parameters['gaistdata'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['PolygonsToLines'] = processing.run('native:polygonstolines', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Dissolve
        alg_params = {
            'FIELD': [''],
            'INPUT': outputs['Difference_missingtopo']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Dissolve'] = processing.run('native:dissolve', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # Extract by expression_mdu
        alg_params = {
            'EXPRESSION': ' "loc_desc"  =  \'MDU\'',
            'INPUT': parameters['demandpoints'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByExpression_mdu'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # Points along geometry
        alg_params = {
            'DISTANCE': 1,
            'END_OFFSET': 0,
            'INPUT': parameters['streetcenterline'],
            'START_OFFSET': 0,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['PointsAlongGeometry'] = processing.run('native:pointsalonglines', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # Extract by location
        alg_params = {
            'INPUT': outputs['Polygonize_topoarea']['OUTPUT'],
            'INTERSECT': outputs['ExtractByExpression_mdu']['OUTPUT'],
            'PREDICATE': [0],  # intersect
            'OUTPUT': parameters['Mdu']
        }
        outputs['ExtractByLocation'] = processing.run('native:extractbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Mdu'] = outputs['ExtractByLocation']['OUTPUT']

        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}

        # Multipart to singleparts
        alg_params = {
            'INPUT': outputs['Dissolve']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['MultipartToSingleparts'] = processing.run('native:multiparttosingleparts', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(8)
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

        feedback.setCurrentStep(9)
        if feedback.isCanceled():
            return {}

        # Merge vector layers_lines
        alg_params = {
            'CRS': QgsCoordinateReferenceSystem('EPSG:27700'),
            'LAYERS': [outputs['PolygonsToLines']['OUTPUT'],outputs['DistanceToNearestHubLineToHub']['OUTPUT'],parameters['streetcenterline']],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['MergeVectorLayers_lines'] = processing.run('native:mergevectorlayers', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(10)
        if feedback.isCanceled():
            return {}

        # Extract by location
        alg_params = {
            'INPUT': outputs['MultipartToSingleparts']['OUTPUT'],
            'INTERSECT': parameters['streetcenterline'],
            'PREDICATE': [0],  # intersect
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByLocation'] = processing.run('native:extractbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(11)
        if feedback.isCanceled():
            return {}

        # Polygonize
        alg_params = {
            'INPUT': outputs['MergeVectorLayers_lines']['OUTPUT'],
            'KEEP_FIELDS': False,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Polygonize'] = processing.run('native:polygonize', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(12)
        if feedback.isCanceled():
            return {}

        # Difference
        alg_params = {
            'INPUT': outputs['MultipartToSingleparts']['OUTPUT'],
            'OVERLAY': outputs['ExtractByLocation']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Difference'] = processing.run('native:difference', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(13)
        if feedback.isCanceled():
            return {}

        # Merge vector layers_land
        alg_params = {
            'CRS': QgsCoordinateReferenceSystem('EPSG:27700'),
            'LAYERS': [outputs['Difference']['OUTPUT'],parameters['landbounadry']],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['MergeVectorLayers_land'] = processing.run('native:mergevectorlayers', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(14)
        if feedback.isCanceled():
            return {}

        # Join attributes by nearest_road
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELDS_TO_COPY': ['cluster_id'],
            'INPUT': outputs['Polygonize']['OUTPUT'],
            'INPUT_2': parameters['clusters'],
            'MAX_DISTANCE': None,
            'NEIGHBORS': 1,
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByNearest_road'] = processing.run('native:joinbynearest', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(15)
        if feedback.isCanceled():
            return {}

        # Join attributes by nearest_land
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELDS_TO_COPY': ['cluster_id'],
            'INPUT': outputs['MergeVectorLayers_land']['OUTPUT'],
            'INPUT_2': parameters['clusters'],
            'MAX_DISTANCE': None,
            'NEIGHBORS': 1,
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByNearest_land'] = processing.run('native:joinbynearest', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(16)
        if feedback.isCanceled():
            return {}

        # Merge vector layers
        alg_params = {
            'CRS': QgsCoordinateReferenceSystem('EPSG:27700'),
            'LAYERS': [outputs['JoinAttributesByNearest_road']['OUTPUT'],outputs['JoinAttributesByNearest_land']['OUTPUT']],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['MergeVectorLayers'] = processing.run('native:mergevectorlayers', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(17)
        if feedback.isCanceled():
            return {}

        # Snap geometries to layer
        alg_params = {
            'BEHAVIOR': 0,  # Prefer aligning nodes, insert extra vertices where required
            'INPUT': outputs['MergeVectorLayers']['OUTPUT'],
            'REFERENCE_LAYER': outputs['MergeVectorLayers']['OUTPUT'],
            'TOLERANCE': 1,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['SnapGeometriesToLayer'] = processing.run('native:snapgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(18)
        if feedback.isCanceled():
            return {}

        # Fix geometries
        alg_params = {
            'INPUT': outputs['SnapGeometriesToLayer']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FixGeometries'] = processing.run('native:fixgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(19)
        if feedback.isCanceled():
            return {}

        # Dissolve
        alg_params = {
            'FIELD': ['cluster_id'],
            'INPUT': outputs['FixGeometries']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Dissolve'] = processing.run('native:dissolve', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(20)
        if feedback.isCanceled():
            return {}

        # Delete holes
        alg_params = {
            'INPUT': outputs['Dissolve']['OUTPUT'],
            'MIN_AREA': 20,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DeleteHoles'] = processing.run('native:deleteholes', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(21)
        if feedback.isCanceled():
            return {}

        # Field calculator
        alg_params = {
            'FIELD_LENGTH': 100,
            'FIELD_NAME': '"struct_id"',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # Text (string)
            'FORMULA': "concat('u',@row_number +1 )",
            'INPUT': outputs['DeleteHoles']['OUTPUT'],
            'OUTPUT': parameters['Ug_boundary']
        }
        outputs['FieldCalculator'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Ug_boundary'] = outputs['FieldCalculator']['OUTPUT']
        return results

    def name(self):
        return 'ug_nodeboundary'

    def displayName(self):
        return 'ug_nodeboundary'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return Ug_nodeboundary()
