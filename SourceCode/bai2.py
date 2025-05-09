import pandas as pd
import matplotlib.pyplot as plt
import os

# ======== 1. Đọc dữ liệu và xử lý chỉ số cần phân tích ========
df = pd.read_csv("results.csv")
columns = ['PrgC', 'PrgR', 'PrgP', 'Save%', 'PK Save%', 'CS%']
teams = df['Team'].unique()

# Chuyển các chỉ số thành số
for col in columns:
    df[col] = pd.to_numeric(df[col].astype(str).str.replace(",", "").replace("N/a", ""), errors='coerce')

# ======== 2. Top 3 cao nhất và thấp nhất mỗi chỉ số ========
with open("top_3.txt", "w", encoding="utf-8") as f:
    for col in columns:
        if df[col].dropna().empty:
            continue
        top_3 = df[['Player', col]].sort_values(by=col, ascending=False).head(3)
        bottom_3 = df[['Player', col]].sort_values(by=col, ascending=True).head(3)

        f.write(f"=== Top 3 for {col} ===\n")
        for _, row in top_3.iterrows():
            f.write(f"{row['Player']}: {row[col]}\n")
        f.write(f"\n=== Bottom 3 for {col} ===\n")
        for _, row in bottom_3.iterrows():
            f.write(f"{row['Player']}: {row[col]}\n")
        f.write("\n" + "="*50 + "\n\n")

print("✅ Đã tạo file top_3.txt")

# ======== 3. Median/Mean/Std toàn giải và từng đội ========
results = []

for col in columns:
    row = {}
    row['Attribute'] = col
    row['Median_all'] = df[col].median()
    row['Mean_all'] = df[col].mean()
    row['Std_all'] = df[col].std()
    for team in teams:
        team_df = df[df['Team'] == team]
        row[f'Mean_{team}'] = team_df[col].mean()
        row[f'Std_{team}'] = team_df[col].std()
    results.append(row)

pd.DataFrame(results).round(3).fillna(0.0).to_csv("results2.csv", index=False)
print("✅ Đã tạo file results2.csv")

# ======== 4. Vẽ biểu đồ histogram từng chỉ số toàn giải và từng đội ========
os.makedirs("histograms", exist_ok=True)

for col in columns:
    # Toàn giải
    plt.figure(figsize=(10,6))
    plt.hist(df[col].dropna(), bins=20, alpha=0.7, color='blue')
    plt.title(f'Distribution of {col} (All Players)')
    plt.xlabel(col)
    plt.ylabel('Frequency')
    plt.grid(True)
    plt.savefig(f'histograms/{col}_all.png')
    plt.close()

    # Từng đội
    for team in teams:
        team_df = df[df['Team'] == team]
        plt.figure(figsize=(10,6))
        plt.hist(team_df[col].dropna(), bins=20, alpha=0.7, color='green')
        plt.title(f'Distribution of {col} ({team})')
        plt.xlabel(col)
        plt.ylabel('Frequency')
        plt.grid(True)
        plt.savefig(f'histograms/{col}_{team}.png')
        plt.close()

print("✅ Đã tạo biểu đồ histogram trong thư mục histograms/")

# ======== 5. Tìm đội có chỉ số cao nhất mỗi tiêu chí ========
best_teams = {}
for col in columns:
    team_means = df.groupby('Team')[col].mean()
    best_team = team_means.idxmax()
    best_teams[col] = best_team

with open("best_teams.txt", "w") as f:
    for stat, team in best_teams.items():
        f.write(f'Top team for {stat}: {team}\n')
print("✅ Đã tạo file best_teams.txt")