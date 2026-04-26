from server import search_clinical_literature
result = search_clinical_literature("dopamine reward prediction error", years_back=5)
print(result[:2000])