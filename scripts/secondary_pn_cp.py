"""
Model exported as python.
Name : secondary_pn_cp
Group : 
With QGIS : 32403
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterFeatureSink
import processing


class Secondary_pn_cp(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('gaist', 'gaist', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('node', 'node', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Pn_cabinets', 'pn_cabinets', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(1, model_feedback)
        results = {}
        outputs = {}

        # pn_cabinetplacement
        alg_params = {
            'gaist': parameters['gaist'],
            'node': parameters['node'],
            'native:snapgeometries_1:pn_cabinets': parameters['Pn_cabinets']
        }
        outputs['Pn_cabinetplacement'] = processing.run('model:pn_cabinetplacement', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Pn_cabinets'] = outputs['Pn_cabinetplacement']['native:snapgeometries_1:pn_cabinets']
        return results

    def name(self):
        return 'secondary_pn_cp'

    def displayName(self):
        return 'secondary_pn_cp'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return Secondary_pn_cp()
