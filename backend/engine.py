import pandas as pd

COL_CO2 = "Adjusted savings: carbon dioxide damage (% of GNI) - NY.ADJ.DCO2.GN.ZS"
COL_GDP = "GDP per capita (current US$) - NY.GDP.PCAP.CD" 
COL_RES = "Adjusted savings: natural resources depletion (% of GNI) - NY.ADJ.DRES.GN.ZS"
COL_POV = "Proportion of population below international poverty line (%) - SI_POV_DAY1 - 1.1.1" 
COL_REN = "Renewable energy consumption (% of total final energy consumption) - EG.FEC.RNEW.ZS"

class SustainabilityEngine:
    def __init__(self, csv_path):
        self.df = pd.read_csv(csv_path)

        self.latest_df = self.df.sort_values('Year').groupby('Country Code').last().reset_index()

        self.stats = {
            'co2': {'min': self.df[COL_CO2].min(), 'max': self.df[COL_CO2].max()},
            'gdp': {'min': self.df[COL_GDP].min(), 'max': self.df[COL_GDP].max()},
            'res': 30, 
            'pov': 50, 
            'ren': 100
        }

    def get_multiplier(self, country_code):
        row = self.latest_df[self.latest_df['Country Code'] == country_code]
        if row.empty: return 1.0, {}

        # 1. Normalized CO2 (25%)
        val_co2 = row[COL_CO2].values[0]
        norm_co2 = (val_co2 - self.stats['co2']['min']) / (self.stats['co2']['max'] - self.stats['co2']['min'])

        # 2. Normalized GDP - INVERSE (20%)
        val_gdp = row[COL_GDP].values[0]
        norm_gdp = 1 - ((val_gdp - self.stats['gdp']['min']) / (self.stats['gdp']['max'] - self.stats['gdp']['min']))

        # 3. Natural Resources Depletion (20%)
        val_res = abs(row[COL_RES].values[0])
        norm_res = min(val_res / self.stats['res'], 1.0)

        # 4. Poverty Rate (15%) - Handling NaN jika data poverty kosong
        val_pov = row[COL_POV].values[0]
        if pd.isna(val_pov): val_pov = 10 # Default average jika data bolong
        norm_pov = min(val_pov / self.stats['pov'], 1.0)

        # 5. Renewable Energy - INVERSE (20%)
        val_ren = row[COL_REN].values[0]
        norm_ren = 1 - min(val_ren / self.stats['ren'], 1.0)

        # Weighted Average Score
        score = (norm_co2 * 0.25) + (norm_gdp * 0.20) + (norm_res * 0.20) + (norm_pov * 0.15) + (norm_ren * 0.20)
        
        # Convert to Multiplier 0.5x - 3.0x
        multiplier = 0.5 + (score * 2.5)
        
        breakdown = {
            "co2": float(norm_co2),
            "gdp_inv": float(norm_gdp),
            "res": float(norm_res),
            "poverty": float(norm_pov),
            "ren_inv": float(norm_ren),
            "score": float(score)
        }
        
        return round(multiplier, 2), breakdown