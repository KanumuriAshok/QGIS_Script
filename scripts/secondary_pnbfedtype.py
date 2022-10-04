"""
Model exported as python.
Name : secondary_pnbfedtype
Group : 
With QGIS : 32403
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterFeatureSink
import processing


class Secondary_pnbfedtype(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('pnboundary', 'pnboundary', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('piastructures', 'piastructures', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Pnboundary', 'pnboundary', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(1, model_feedback)
        results = {}
        outputs = {}

        # pn_fedtype
        alg_params = {
            'piastructures': parameters['piastructures'],
            'pnboundary': parameters['pnboundary'],
            'native:fieldcalculator_1:pnboundary': parameters['Pnboundary']
        }
        outputs['Pn_fedtype'] = processing.run('model:pn_fedtype', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Pnboundary'] = outputs['Pn_fedtype']['native:fieldcalculator_1:pnboundary']
        return results

    def name(self):
        return 'secondary_pnbfedtype'

    def displayName(self):
        return 'secondary_pnbfedtype'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return Secondary_pnbfedtype()
