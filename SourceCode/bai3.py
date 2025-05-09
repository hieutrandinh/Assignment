import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import seaborn as sns

# Đọc dữ liệu
df = pd.read_csv('results.csv')

# Chuyển 'N/a' thành NaN và ép kiểu numeric cho các cột số
df.replace('N/a', np.nan, inplace=True)

# Xác định các cột số
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

# Nếu chưa có numeric cols — ép kiểu thử các cột còn lại
if not numeric_cols:
    for col in df.columns:
        try:
            df[col] = pd.to_numeric(df[col])
        except:
            continue
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

# Loại bỏ các hàng bị thiếu dữ liệu
df.dropna(subset=numeric_cols, inplace=True)

# Chuẩn hóa dữ liệu
scaler = StandardScaler()
X_scaled = scaler.fit_transform(df[numeric_cols])

# Tìm số cluster tối ưu bằng Elbow Method
inertia = []
K_range = range(1, 11)
for k in K_range:
    kmeans = KMeans(n_clusters=k, n_init=10, random_state=42)
    kmeans.fit(X_scaled)
    inertia.append(kmeans.inertia_)

# Vẽ biểu đồ Elbow
plt.figure(figsize=(8, 5))
plt.plot(K_range, inertia, 'bo-')
plt.xlabel('Number of Clusters (k)')
plt.ylabel('Inertia')
plt.title('Elbow Method for Optimal k')
plt.grid()
plt.show()

# Chọn số cluster — ví dụ k=3 từ Elbow Method
k = 3
kmeans = KMeans(n_clusters=k, n_init=10, random_state=42)
clusters = kmeans.fit_predict(X_scaled)

# Thêm cột cluster vào dataframe
df['Cluster'] = clusters

# Giảm chiều dữ liệu xuống 2D với PCA
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)

# Thêm PCA vào dataframe
df['PCA1'] = X_pca[:, 0]
df['PCA2'] = X_pca[:, 1]

# Vẽ scatter plot các nhóm
plt.figure(figsize=(8, 6))
sns.scatterplot(data=df, x='PCA1', y='PCA2', hue='Cluster', palette='Set1')
plt.title(f'K-means Clustering with k={k} (PCA 2D)')
plt.xlabel('Principal Component 1')
plt.ylabel('Principal Component 2')
plt.legend(title='Cluster')
plt.grid(True)
plt.show()
