import os
import tempfile
import pandas as pd
from datetime import datetime
from .scraper import scrape_smcaen_matches

def get_current_year():
    """Return current year"""
    return datetime.now().year

def extract_caen_data(annee_debut, annee_fin, output_format='xlsx'):
    """
    Extract SM Caen data for a given year range.
    
    Args:
        annee_debut (int): Start year
        annee_fin (int): End year
        output_format (str): Output format ('xlsx' or 'csv')
    
    Returns:
        str: Path to output file
    """
    
    validate_years(annee_debut, annee_fin)

    # Business rule:
    # - annee_debut = start year of season
    # - annee_fin = end year of season
    # Example: 2021 -> 2022 => only season 2021-2022
    season_start = annee_debut
    season_end = annee_fin - 1

    # Get real data from official website
    df = scrape_smcaen_matches(season_start, season_end)
    if df.empty:
        raise ValueError("No match data found for this year range")
    
    # Generate output file
    output_dir = tempfile.gettempdir()
    output_filename = f'caen_data_{annee_debut}_{annee_fin}.{output_format}'
    output_path = os.path.join(output_dir, output_filename)
    
    if output_format == 'xlsx':
        df.to_excel(output_path, index=False, engine='openpyxl')
    elif output_format == 'csv':
        df.to_csv(output_path, index=False)
    else:
        raise ValueError(f"Unsupported output format: {output_format}")
    
    return output_path

def get_available_years():
    """
    Return available year range for extraction.
    Max year is always current year.
    
    Returns:
        tuple: (min_year, max_year)
    """
    current_year = get_current_year()
    return (2012, current_year)

def validate_years(annee_debut, annee_fin):
    """
    Validate provided years.
    
    Args:
        annee_debut (int): Start year
        annee_fin (int): End year
    
    Raises:
        ValueError: If years are not valid
    """
    min_year, max_year = get_available_years()
    
    if annee_debut < min_year or annee_debut > max_year:
        raise ValueError(f"Start year must be between {min_year} and {max_year}")
    
    # End year represents end of season, so must be strictly
    # greater than start year (e.g., 2021 -> 2022)
    min_end_year = min_year + 1
    if annee_fin < min_end_year or annee_fin > (max_year + 1):
        raise ValueError(f"End year must be between {min_end_year} and {max_year + 1}")
    
    if annee_debut >= annee_fin:
        raise ValueError("End year must be strictly greater than start year")
