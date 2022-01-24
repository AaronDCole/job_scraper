from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from typing import Optional
import io

from adzuna_engine import AdzunaEngine
from indeed_engine import IndeedEngine
from indeed_engine import CaptchaException

# incl_all, incl_exact, incl_at_least_one, excl_words, incl_title, salary_lower, salary_higher, employment_hours, contract_type, results_pp
# https://www.adzuna.com.au/search?adv=1&qwd={incl_all}&qph={incl_exact}&qor={incl_at_least_one}&qxl=excl_words&qtl=in_title&sf=5000&st=140000&cty=permanent&cti=full_time&w=Australia&pp=50&sb=date&sd=down

app = FastAPI()

@app.get("/adzuna/incl_title_terms")
async def adz_search_incl_title_terms(terms: str):
    # Generate a new adzuna_engine instance
    adzuna_engine = AdzunaEngine()
    adzuna_engine.query_contents['qtl'] = terms

    # Pagination
    n_pages = adzuna_engine.get_query_pages()

    if n_pages == 0:
        return {"status" : False, 
        "message" : "No jobs found for that query"}

    # Data structures
    listing_list = [] 
    listings_dict = {}

    # Run the queries
    output_df = await adzuna_engine.collate_data(listings_dict, listing_list, n_pages)

    # Return a data stream
    response = StreamingResponse(io.StringIO(output_df.to_csv(index=False)), media_type="text/csv")
    # Edit the headers so its a download
    response.headers["Content-Disposition"] = "attachment; filename=export.csv"

    return response 


@app.get("/indeed/incl_title_terms")
async def ind_search_incl_title_terms(terms: str):
    # Generate a new adzuna_engine instance
    indeed_engine = IndeedEngine()
    indeed_engine.searchq = terms

    # Pagination
    try:
        n_pages = indeed_engine.get_query_pages()
    except CaptchaException as e:
        return {"status" : False, 
            "message" : str(e)}

    if n_pages == 0:
        return {"status" : False, 
            "message" : "No jobs found for that query"}

    # Data structures
    listing_list = [] 
    listings_dict = {}

    # Run the queries
    output_df = await indeed_engine.collate_data(listings_dict, listing_list, n_pages)

    # Return a data stream
    response = StreamingResponse(io.StringIO(output_df.to_csv(index=False)), media_type="text/csv")
    # Edit the headers so its a download
    response.headers["Content-Disposition"] = "attachment; filename=export.csv"

    return response 