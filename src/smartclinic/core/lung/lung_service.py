import joblib
import numpy as np

from smartclinic.core.lung.lung_dto import PredictLung

scaler_path = r"models/model_normalize/ScalerUngThuPhoi12.pkl"
model_path = r'models/model_predict/KNNUngThuPhoi12.pkl'

loaded_model = joblib.load(model_path)
scaler = joblib.load(scaler_path)


def process_prediction(data: PredictLung):
    if data.Age == 0:
        return 0, "Không có khả năng bị ung thư khi tuổi là 0"
        
    feature_vector = [
        data.Age,
        data.Gender,
        data.Air_Pollution,
        data.Alcohol_use,
        data.OccuPational_Hazards,
        data.Genetic_Risk,
        data.chronic_Lung_Disease,
        data.Smoking,
        data.Passive_Smoker,
        data.Chest_Pain,
        data.Coughing_of_Blood,
        data.Clubbing_of_Finger_Nails
    ]
    
    input_data = np.array([feature_vector])

    input_data_scaled = scaler.transform(input_data)
    
    y_pred = loaded_model.predict(input_data_scaled)
    
    if y_pred[0] == 1:
        result = 'Khả năng bị ung thư thấp'
    elif y_pred[0] == 2:
        result = 'Khả năng ung thư ở mức độ vừa phải'
    elif y_pred[0] == 3:
        result = 'Khả năng cao mắc bệnh ung thư'
    else:
        result = 'Không rõ nguyên nhân'
    return int(y_pred[0]), result