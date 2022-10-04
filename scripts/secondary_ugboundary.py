"""
Model exported as python.
Name : secondary_ugboundary
Group : 
With QGIS : 32403
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterFeatureSink
import processing


class Secondary_ugboundary(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('clusters', 'clusters', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('topographiclines', 'topographiclines', types=[QgsProcessing.TypeVectorLine], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('landbounadry', 'landbounadry', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('demandpoints', 'demandpoints', defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('gaistdata', 'gaistdata', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('streetcenterline', 'streetcenterline', types=[QgsProcessing.TypeVectorLine], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Mdu', 'mdu', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Ug_boundary', 'ug_boundary', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(1, model_feedback)
        results = {}
        outputs = {}

        # ug_nodeboundary
        alg_params = {
            'clusters': parameters['clusters'],
            'demandpoints': parameters['demandpoints'],
            'gaistdata': parameters['gaistdata'],
            'landbounadry': parameters['landbounadry'],
            'streetcenterline': parameters['streetcenterline'],
            'topographiclines': parameters['topographiclines'],
            'native:extractbylocation_2:mdu': parameters['Mdu'],
            'native:fieldcalculator_1:ug_boundary': parameters['Ug_boundary']
        }
        outputs['Ug_nodeboundary'] = processing.run('model:ug_nodeboundary', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Mdu'] = outputs['Ug_nodeboundary']['native:extractbylocation_2:mdu']
        results['Ug_boundary'] = outputs['Ug_nodeboundary']['native:fieldcalculator_1:ug_boundary']
        return results

    def name(self):
        return 'secondary_ugboundary'

    def displayName(self):
        return 'secondary_ugboundary'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return Secondary_ugboundary()
