import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import os
import logging
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from scipy.stats import spearmanr, randint, uniform
from math import sqrt
import xgboost as xgb

# Cài đặt môi trường và hiển thị
warnings.filterwarnings("ignore")
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
logging.getLogger('sklearn').setLevel(logging.CRITICAL)
plt.style.use('ggplot')

# --- Load dữ liệu ---
def load_data():
    features = pd.read_csv("results.csv")
    values = pd.read_csv("transfer_values.csv")

    # Chuẩn hóa tên cầu thủ
    for df in [features, values]:
        df["Player"] = df["Player"].str.strip().str.lower()

    # Merge theo "Player"
    merged = pd.merge(features, values, on="Player", how="inner", suffixes=('', '_drop'))
    merged = merged.filter(regex='^(?!.*_drop)')  # Bỏ các cột bị trùng

    return merged

# --- Tiền xử lý dữ liệu ---
def preprocess_data(df):
    # Chuyển đổi giá trị từ dạng "€10m" -> 10_000_000
    def convert_value(value):
        try:
            value = str(value).lower().replace("€", "").replace(",", "").strip()
            if 'm' in value:
                return float(value.replace('m', '')) * 1e6
            if 'k' in value:
                return float(value.replace('k', '')) * 1e3
            return float(value)
        except:
            return np.nan

    df["Value"] = df["Value"].apply(convert_value)
    df = df[df["Value"] > 1000]  # Loại bỏ cầu thủ không có giá trị thực

    # Chuyển các cột bắt buộc sang số nếu chưa đúng kiểu
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    for col in ['Goals', 'Assists', 'Age']:
        if col in df.columns and col not in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            numeric_cols.append(col)

    # Thêm đặc trưng mới
    df['Goals_per_Age'] = df['Goals'] / df['Age']
    df['Assists_per_Age'] = df['Assists'] / df['Age']
    df['Log_Transfer_Value'] = np.log1p(df['Value'])

    # Xử lý missing value
    df[['Goals_per_Age', 'Assists_per_Age']] = df[['Goals_per_Age', 'Assists_per_Age']].fillna(0)
    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())

    return df

# --- Xây dựng pipeline model ---
def build_model(numeric_features):
    preprocessor = ColumnTransformer(transformers=[
        ('num', StandardScaler(), numeric_features)
    ])

    model = Pipeline([
        ('preprocessor', preprocessor),
        ('regressor', xgb.XGBRegressor(objective='reg:squarederror', random_state=42, n_jobs=-1, verbosity=0))
    ])

    return model

# --- Đánh giá mô hình ---
def evaluate_model(model, X, y, log_target=True):
    pred = model.predict(X)
    if log_target:
        y_true = np.expm1(y)
        pred = np.expm1(pred)
    else:
        y_true = y

    rmse = sqrt(mean_squared_error(y_true, pred))
    mae = mean_absolute_error(y_true, pred)
    r2 = r2_score(y_true, pred)
    spear_corr, _ = spearmanr(y_true, pred)

    print(f"  R2 Score: {r2:.4f}")
    print(f"  RMSE: {rmse / 1e6:.4f} triệu €")
    print(f"  MAE: {mae / 1e6:.4f} triệu €")
    print(f"  Spearman Corr: {spear_corr:.4f}")

# --- Chạy chính ---
if __name__ == "__main__":
    df = load_data()
    df = preprocess_data(df)

    # Tách biến đầu vào và đầu ra
    X = df.drop(columns=['Value', 'Log_Transfer_Value', 'Player'])
    y = df['Log_Transfer_Value']
    numeric_features = X.select_dtypes(include=np.number).columns.tolist()

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = build_model(numeric_features)

    # Random search để tối ưu tham số
    param_dist = {
        'regressor__n_estimators': randint(100, 400),
        'regressor__learning_rate': uniform(0.05, 0.2),
        'regressor__max_depth': randint(4, 8),
        'regressor__subsample': uniform(0.7, 0.3),
        'regressor__colsample_bytree': uniform(0.7, 0.3)
    }

    search = RandomizedSearchCV(model, param_dist, n_iter=15, cv=3,
                                scoring='neg_root_mean_squared_error',
                                random_state=42, n_jobs=-1)
    search.fit(X_train, y_train)
    best_model = search.best_estimator_

    print("\nĐánh giá trên tập huấn luyện:")
    evaluate_model(best_model, X_train, y_train)

    print("\nĐánh giá trên tập kiểm tra:")
    evaluate_model(best_model, X_test, y_test)
