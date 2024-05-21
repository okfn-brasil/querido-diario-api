import uvicorn

from api import app, configure_api_app
from cities import create_cities_data_gateway, create_cities_interface
from config import load_configuration
from companies import create_companies_interface
from aggregates import create_aggregates_interface
from database import create_companies_database_interface, create_aggregates_database_interface
from gazettes import (
    create_gazettes_interface,
    create_gazettes_data_gateway,
    create_gazettes_query_builder,
)
from index import create_search_engine_interface
from suggestions import create_suggestion_service
from themed_excerpts import (
    create_themes_database_gateway,
    create_themed_excerpts_data_gateway,
    create_themed_excerpts_interface,
    create_themed_excerpts_query_builder,
)

configuration = load_configuration()

search_engine = create_search_engine_interface(
    configuration.host, (configuration.opensearch_user, configuration.opensearch_pswd), configuration.gazette_index
)

gazettes_query_builder = create_gazettes_query_builder(
    configuration.gazette_content_field,
    configuration.gazette_content_exact_field_suffix,
    configuration.gazette_publication_date_field,
    configuration.gazette_scraped_at_field,
    configuration.gazette_territory_id_field,
)
gazettes_search_engine_gateway = create_gazettes_data_gateway(
    search_engine, gazettes_query_builder, configuration.gazette_index
)
gazettes_interface = create_gazettes_interface(gazettes_search_engine_gateway)

themed_excerpts_query_builder = create_themed_excerpts_query_builder(
    configuration.themed_excerpt_content_field,
    configuration.themed_excerpt_content_exact_field_suffix,
    configuration.themed_excerpt_publication_date_field,
    configuration.themed_excerpt_scraped_at_field,
    configuration.themed_excerpt_territory_id_field,
    configuration.themed_excerpt_entities_field,
    configuration.themed_excerpt_subthemes_field,
    configuration.themed_excerpt_embedding_score_field,
    configuration.themed_excerpt_tfidf_score_field,
    configuration.themed_excerpt_fragment_size,
    configuration.themed_excerpt_number_of_fragments,
)
themed_excerpts_search_engine_gateway = create_themed_excerpts_data_gateway(
    search_engine, themed_excerpts_query_builder
)
themes_database_gateway = create_themes_database_gateway(
    configuration.themes_database_file
)
themed_excerpts_interface = create_themed_excerpts_interface(
    themed_excerpts_search_engine_gateway, themes_database_gateway
)

cities_database_gateway = create_cities_data_gateway(configuration.city_database_file)
cities_interface = create_cities_interface(cities_database_gateway)

suggestion_service = create_suggestion_service(
    suggestion_mailjet_rest_api_key=configuration.suggestion_mailjet_rest_api_key,
    suggestion_mailjet_rest_api_secret=configuration.suggestion_mailjet_rest_api_secret,
    suggestion_sender_name=configuration.suggestion_sender_name,
    suggestion_sender_email=configuration.suggestion_sender_email,
    suggestion_recipient_name=configuration.suggestion_recipient_name,
    suggestion_recipient_email=configuration.suggestion_recipient_email,
    suggestion_mailjet_custom_id=configuration.suggestion_mailjet_custom_id,
)
companies_database = create_companies_database_interface(
    db_host=configuration.companies_database_host,
    db_name=configuration.companies_database_db,
    db_user=configuration.companies_database_user,
    db_pass=configuration.companies_database_pass,
    db_port=configuration.companies_database_port,
)
companies_interface = create_companies_interface(companies_database)
aggregates_database = create_aggregates_database_interface(
    db_host=configuration.aggregates_database_host,
    db_name=configuration.aggregates_database_db,
    db_user=configuration.aggregates_database_user,
    db_pass=configuration.aggregates_database_pass,
    db_port=configuration.aggregates_database_port,
)
aggregates_interface = create_aggregates_interface(aggregates_database)

configure_api_app(
    gazettes_interface,
    themed_excerpts_interface,
    cities_interface,
    suggestion_service,
    companies_interface,
    aggregates_interface,
    configuration.root_path
)

uvicorn.run(app, host="0.0.0.0", port=8080, root_path=configuration.root_path)
