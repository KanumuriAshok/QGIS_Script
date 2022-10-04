"""
Model exported as python.
Name : pn_fedtype
Group : 
With QGIS : 32403
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterFeatureSink
import processing


class Pn_fedtype(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('pnboundary', 'pnboundary', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('piastructures', 'piastructures', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Pnboundary', 'pnboundary', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(3, model_feedback)
        results = {}
        outputs = {}

        # Extract by expression
        alg_params = {
            'EXPRESSION': ' "category"  = \'POLE\'',
            'INPUT': parameters['piastructures'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByExpression'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Count points in polygon
        alg_params = {
            'CLASSFIELD': '',
            'FIELD': 'polecount',
            'POINTS': outputs['ExtractByExpression']['OUTPUT'],
            'POLYGONS': parameters['pnboundary'],
            'WEIGHT': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['CountPointsInPolygon'] = processing.run('native:countpointsinpolygon', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Field calculator
        alg_params = {
            'FIELD_LENGTH': 100,
            'FIELD_NAME': 'fedtype',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # Text (string)
            'FORMULA': 'if( "polecount" >0 ,\'aerial\',\'ug\')',
            'INPUT': outputs['CountPointsInPolygon']['OUTPUT'],
            'OUTPUT': parameters['Pnboundary']
        }
        outputs['FieldCalculator'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Pnboundary'] = outputs['FieldCalculator']['OUTPUT']
        return results

    def name(self):
        return 'pn_fedtype'

    def displayName(self):
        return 'pn_fedtype'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return Pn_fedtype()
