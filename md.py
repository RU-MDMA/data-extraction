import pandas as pd
import os

def analyze(input_path):# קריאת קובץ המטא-דאטה
    df = pd.read_csv(input_path)

# נוודא שאין רווחים מיותרים בשמות המטופלים והפגישות
    df['subject'] = df['subject'].astype(str).str.strip()
    df['meet'] = df['meet'].astype(str).str.strip()

# ניצור תיקיה ליצוא הקבצים אם לא קיימת
    output_dir = "patients_excel"
    os.makedirs(output_dir, exist_ok=True)

# נזהה את כל המטופלים הייחודיים
    for subject in df['subject'].unique():
        subject_df = df[df['subject'] == subject]

    # נתחיל כתיבה של קובץ אקסל חדש למטופל
        file_name = f"{output_dir}/patient_{subject.replace(' ', '_')}.xlsx"
        with pd.ExcelWriter(file_name, engine='openpyxl') as writer:
            for meet in subject_df['meet'].unique():
                meet_df = subject_df[subject_df['meet'] == meet]

            # ניקוי שם ה-Sheet מתווים אסורים
                sheet_name = meet.replace(' ', '_')[:31]  # Excel מגביל ל-31 תווים
                meet_df.to_excel(writer, sheet_name=sheet_name, index=False)

    print("✔️ הסתיים ייצור קבצי האקסל לכל מטופל.")
