import pandas as pd
import matplotlib.pyplot as plt
import os

# ======== 1. Đọc dữ liệu và xử lý chỉ số cần phân tích ========
df = pd.read_csv("results.csv")
columns = ['Age', 'Matches Played', 'Starts', 'Minutes', 'Goals', 'Assists', 'Yellow Cards', 'Red Cards',
           'xG', 'xAG', 'PrgC', 'PrgP', 'PrgR', 'Gls90', 'Ast90', 'xG90', 'xAG90', 'GA90', 'Save%', 
           'CS%', 'PK Save%', 'SoT%', 'SoT/90', 'G/Sh', 'Dist', 'Cmp', 'Cmp%', 'TotDist', 'Cmp% (Short)', 
           'Cmp% (Medium)', 'Cmp% (Long)', 'KP', 'Passes 1/3', 'PPA', 'CrsPA', 'SCA', 'SCA90', 'GCA', 'GCA90', 
           'Tkl', 'TklW', 'Att', 'Challenges Lost', 'Blocks', 'Sh', 'Pass', 'Int', 'Touches', 'Def Pen', 
           'Def 3rd', 'Mid 3rd', 'Att 3rd', 'Att Pen', 'Att (TO)', 'Succ%', 'Tkld%', 'Carries', 'ProDist', 
           'ProgC', 'Carries 1/3', 'CPA', 'Mis', 'Dis', 'Rec', 'Fls', 'Fld', 'Off', 'Crs', 'Recov', 'Won', 
           'Aerials Lost', 'Won%']
teams = df['Team'].unique()

# ======== 2. Chuyển đổi giá trị "Age" sang số năm ========
def convert_age_to_years(age_str):
    try:
        # Tách tuổi và số ngày
        age, days = age_str.split('-')
        age = int(age)
        days = int(days)
        # Tính tuổi tính theo năm, cộng thêm phần năm từ số ngày
        return age + (days / 365.25)
    except Exception as e:
        print(f"Lỗi khi chuyển đổi tuổi {age_str}: {e}")
        return 0  # Trả về 0 nếu không thể chuyển đổi

# Áp dụng hàm chuyển đổi cho cột 'Age'
df['Age'] = df['Age'].apply(convert_age_to_years)

# ======== 3. Chuyển đổi các cột còn lại về kiểu số ========
for col in columns:
    df[col] = pd.to_numeric(df[col].astype(str).str.replace(",", "").replace("N/a", "0"), errors='coerce')
# ======== 4. Top 3 cao nhất và thấp nhất mỗi chỉ số ========
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

# ======== 5. Median/Mean/Std theo đội bóng ========
results = []

# Kiểm tra giá trị hợp lệ trong mỗi đội
for team in teams:
    row = {'Team': team}
    for col in columns:
        team_df = df[df['Team'] == team]
        
        # Kiểm tra xem dữ liệu trong cột có hợp lệ
        valid_values = team_df[col].dropna()
        if not valid_values.empty:
            # Tính các chỉ số nếu có giá trị hợp lệ
            row[f'Median of {col}'] = valid_values.median()
            row[f'Mean of {col}'] = valid_values.mean()
            row[f'Std of {col}'] = valid_values.std()
        else:
            # Nếu không có giá trị hợp lệ, gán giá trị mặc định
            row[f'Median of {col}'] = 0.0
            row[f'Mean of {col}'] = 0.0
            row[f'Std of {col}'] = 0.0
            
    results.append(row)

# Lưu kết quả vào file CSV
pd.DataFrame(results).round(3).fillna(0.0).to_csv("results2.csv", index=False)
print("✅ Đã tạo file results2.csv")

# ======== 6. Tìm đội có chỉ số cao nhất mỗi tiêu chí ========
best_teams = {}
for col in columns:
    team_means = df.groupby('Team')[col].mean()
    best_team = team_means.idxmax()
    best_teams[col] = best_team

with open("best_teams.txt", "w") as f:
    for stat, team in best_teams.items():
        f.write(f'Top team for {stat}: {team}\n')

print("✅ Đã tạo file best_teams.txt")

# ======== 7. Vẽ biểu đồ histogram từng chỉ số toàn giải và từng đội ========
df = pd.read_csv("results.csv")
columns = ['PrgC', 'PrgR', 'PrgP', 'Save%', 'PK Save%', 'CS%']
teams = df['Team'].unique()
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