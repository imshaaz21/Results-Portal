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
        try:
            # Remove unwanted rows and reset the index
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
        except Exception as e:
            raise ValueError(f"Error while processing the sheet: {e}")

    def upload_file(self, file):
        """Upload and store the Excel file data, cleaning the sheets and combining them."""
        try:
            # Load the sheets, make sure the sheets exist
            self.physical_science_df = pd.read_excel(file, sheet_name="Physical Science")
            self.biological_science_df = pd.read_excel(file, sheet_name="Biological Science")

            # Clean each sheet
            physical_science_cleaned = DataProcessor.clean_sheet(self.physical_science_df, is_physical_science=True)
            biological_science_cleaned = DataProcessor.clean_sheet(self.biological_science_df,
                                                                   is_physical_science=False)

            # Check if cleaning was successful
            if physical_science_cleaned is None or biological_science_cleaned is None:
                raise ValueError("One or both sheets could not be processed. Please check the file format.")

            # Combine the data
            self.combined_df = pd.concat([physical_science_cleaned, biological_science_cleaned], ignore_index=True)

            # Reorder the columns
            desired_column_order = [
                'Index_Number', 'Name_with_Initial', 'Zone', 'Stream', 'School',
                'Combined_Maths', 'Biology', 'Chemistry', 'Physics', 'Z-Score', 'Rank'
            ]
            self.combined_df = self.combined_df[desired_column_order]

        except FileNotFoundError:
            raise FileNotFoundError("The uploaded file could not be found. Please upload the correct file.")
        except ValueError as ve:
            raise ValueError(f"File format error: {ve}")
        except Exception as e:
            raise RuntimeError(f"An unexpected error occurred during file upload: {e}")

    def has_data(self):
        """Check if data is available."""
        return self.combined_df is not None

    def extract_zones(self):
        """Extract unique zones from the combined data."""
        try:
            if self.combined_df is not None:
                return sorted(self.combined_df['Zone'].dropna().unique())
            return []
        except Exception as e:
            raise RuntimeError(f"Error while extracting zones: {e}")

    def grade_summary(self, zone):
        """Summarize grades A, B, C, S, F by zone for each subject."""
        try:
            grade_counts = {'Chemistry': {}, 'Physics': {}, 'Combined_Maths': {}, 'Biology': {}}
            grades = ['A', 'B', 'C', 'S', 'F']

            zone_data = self.combined_df[self.combined_df['Zone'] == zone]

            # Summarize grades for each subject
            for subject in grade_counts:
                for grade in grades:
                    grade_counts[subject][grade] = zone_data[zone_data[subject] == grade].shape[0]

            return grade_counts
        except KeyError:
            raise KeyError("Grade data for the selected zone or subject could not be found.")
        except Exception as e:
            raise RuntimeError(f"Error while summarizing grades: {e}")

    def search_results(self, zone, index_no):
        """Find a student result based on zone and index number."""
        try:
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

            raise ValueError("No results found for the given index number and zone.")

        except KeyError as e:
            raise KeyError(f"Missing column in the data: {e}")
        except Exception as e:
            raise RuntimeError(f"Error while searching for student results: {e}")
