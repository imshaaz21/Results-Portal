import pandas as pd
import numpy as np


class DataProcessor:
    def __init__(self):
        self.physical_science_df = None
        self.biological_science_df = None
        self.combined_df = None

    @staticmethod
    def clean_sheet(df, is_physical_science=True):
        """Cleans and processes the individual sheets for Physical and Biological Science."""
        df = df.iloc[1:].reset_index(drop=True)

        df.iloc[0, -1] = 'Rank'
        df.iloc[0, -2] = 'Z-Score'
        df.drop(columns=[df.columns[-3]], inplace=True)

        df.columns = df.iloc[0]
        df = df.iloc[1:].reset_index(drop=True)

        df.columns = df.columns.str.replace(' ', '_')

        # Drop unnecessary columns
        columns_to_remove = [col for col in df.columns if col.startswith('Part') or col.startswith('Total')]
        df.drop(columns=columns_to_remove, inplace=True)

        # Define the last columns to retain
        last_columns = ['Chemistry', 'Physics', 'Combined_Maths' if is_physical_science else 'Biology', 'Z-Score',
                        'Rank']
        df.columns = list(df.columns[:-5]) + last_columns

        if is_physical_science:
            df['Biology'] = np.nan
        else:
            df['Combined_Maths'] = np.nan

        return df

    def upload_file(self, file):
        """Upload and store the Excel file data, cleaning the sheets and combining them."""
        # Load the sheets
        self.physical_science_df = pd.read_excel(file, sheet_name="Physical Science")
        self.biological_science_df = pd.read_excel(file, sheet_name="Biological Science")

        # Clean each sheet
        physical_science_cleaned = DataProcessor.clean_sheet(self.physical_science_df, is_physical_science=True)
        biological_science_cleaned = DataProcessor.clean_sheet(self.biological_science_df, is_physical_science=False)

        # Combine the data
        self.combined_df = pd.concat([physical_science_cleaned, biological_science_cleaned], ignore_index=True)

        # Reorder the columns
        desired_column_order = [
            'Index_Number', 'Name_with_Initial', 'Zone', 'Stream', 'School',
            'Combined_Maths', 'Biology', 'Chemistry', 'Physics', 'Z-Score', 'Rank'
        ]
        self.combined_df = self.combined_df[desired_column_order]

    def has_data(self):
        """Check if data is available."""
        return self.combined_df is not None

    def extract_zones(self):
        """Extract unique zones from the combined data."""
        if self.combined_df is not None:
            return sorted(self.combined_df['Zone'].dropna().unique())
        return []

    def grade_summary(self, zone):
        """Summarize grades A, B, C, S, F by zone for each subject."""
        grade_counts = {'Chemistry': {}, 'Physics': {}, 'Combined_Maths': {}, 'Biology': {}}
        grades = ['A', 'B', 'C', 'S', 'F']

        zone_data = self.combined_df[self.combined_df['Zone'] == zone]

        # Summarize grades for each subject
        for subject in grade_counts:
            for grade in grades:
                grade_counts[subject][grade] = zone_data[zone_data[subject] == grade].shape[0]

        return grade_counts

    def overall_grade_summary(self):
        """Get overall grade summary across all zones."""
        grade_counts = {'Chemistry': {}, 'Physics': {}, 'Combined_Maths': {}, 'Biology': {}}
        grades = ['A', 'B', 'C', 'S', 'F']

        # Summarize grades for each subject
        for subject in grade_counts:
            for grade in grades:
                grade_counts[subject][grade] = self.combined_df[self.combined_df[subject] == grade].shape[0]

        return grade_counts

    def search_results(self, zone, index_no):
        """Find a student result based on zone and index number."""
        print(f"Shape of combined: {self.combined_df.shape[0]}")
        print(f"zone, index: {zone}, {index_no}")

        # Convert Index_Number to string and strip whitespace before comparison
        self.combined_df['Index_Number'] = self.combined_df['Index_Number'].astype(str).str.strip()

        # Strip the index_no input as well, in case it has extra spaces
        index_no = str(index_no).strip()

        # Find student data
        student_data = self.combined_df[
            (self.combined_df['Zone'] == zone) & (self.combined_df['Index_Number'] == index_no)]

        if not student_data.empty:
            # Check the stream and drop unnecessary columns
            if student_data['Stream'].iloc[0] == 'Physical Science':
                # Drop the Biology column if the stream is Physical Science
                student_data = student_data.drop(columns=['Biology'], errors='ignore')
            else:
                # Drop Physics and Chemistry columns if the stream is not Physical Science
                student_data = student_data.drop(columns=['Combined_Maths'], errors='ignore')

            return student_data.to_dict(orient='records')[0]

        return None
