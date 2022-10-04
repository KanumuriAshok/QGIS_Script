"""
Model exported as python.
Name : addressCreationNew
Group : 
With QGIS : 31616
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterFeatureSink
from qgis.core import QgsProcessingParameterBoolean
import processing


class Addresscreationnew(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('DemandPoints', 'demandpoints', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('Onexisting', 'on_existing', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('Proposed', 'proposed', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Address', 'Address', optional=True, type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterBoolean('VERBOSE_LOG', 'Verbose logging', optional=True, defaultValue=False))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(4, model_feedback)
        results = {}
        outputs = {}

        # Field calculator
        alg_params = {
            'FIELD_LENGTH': 30,
            'FIELD_NAME': 'conc',
            'FIELD_PRECISION': 30,
            'FIELD_TYPE': 2,
            'FORMULA': ' concat(  \"postcode\" ,\',\', \"bld_num\" ,\'- \', \"streetname\" )',
            'INPUT': parameters['DemandPoints'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FieldCalculator'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Convert multipoints to points
        alg_params = {
            'MULTIPOINTS': parameters['Proposed'],
            'POINTS': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ConvertMultipointsToPoints'] = processing.run('saga:convertmultipointstopoints', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Union
        alg_params = {
            'INPUT': outputs['ConvertMultipointsToPoints']['POINTS'],
            'OVERLAY': parameters['Onexisting'],
            'OVERLAY_FIELDS_PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Union'] = processing.run('native:union', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Join attributes by nearest
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELDS_TO_COPY': ['conc'],
            'INPUT': outputs['Union']['OUTPUT'],
            'INPUT_2': outputs['FieldCalculator']['OUTPUT'],
            'MAX_DISTANCE': None,
            'NEIGHBORS': 1,
            'PREFIX': '',
            'OUTPUT': parameters['Address']
        }
        outputs['JoinAttributesByNearest'] = processing.run('native:joinbynearest', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Address'] = outputs['JoinAttributesByNearest']['OUTPUT']
        return results

    def name(self):
        return 'addressCreationNew'

    def displayName(self):
        return 'addressCreationNew'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return Addresscreationnew()
