import pytest

from http import HTTPStatus
from datetime import date, datetime, timedelta



class TestsApiGazettesEndpoint:
    def test_api_should_fail_when_try_to_set_any_object_as_gazettes_interface(self, mocker, configure_app):
        with pytest.raises(Exception):
            configure_app(
                gazette=mocker.Mock()
            )
    
    def test_api_should_not_fail_when_try_to_set_any_object_as_gazettes_interface(self, configure_app):
        configure_app() #TODO: ver se seria legal colocar um spy 

    def test_gazettes_endpoint_should_accept_territory_id_in_the_path(self, mock_gazette_interface, configure_app, client):
        interface = mock_gazette_interface()

        configure_app(
            gazettes=interface
        )
        
        response = client.get("/gazettes", params={"territory_ids": "4205902"}) #TODO: remover isso e colocar de volta a assert na interface
        
        assert response.status_code == HTTPStatus.OK
        assert response.json() == {"total_gazettes": 0, "gazettes": []}

    def test_gazettes_endpoint_should_accept_query_published_since_date(self, mock_gazette_interface, configure_app, client):
        interface = mock_gazette_interface()

        configure_app(
            gazettes=interface
        )
        
        response = client.get(
            "/gazettes",
            params={"territory_ids": "4205902","published_since": date.today().isoformat()}
        )
        
        assert response.status_code == HTTPStatus.OK

    def test_gazettes_endpoint_should_accept_query_published_until_date(self, mock_gazette_interface, configure_app, client):
        interface = mock_gazette_interface()

        configure_app(
            gazettes=interface
        )
        
        response = client.get(
            "/gazettes",
            params={"territory_ids": "4205902","published_until": date.today().isoformat()}
        )

        assert response.status_code == HTTPStatus.OK

    def test_gazettes_endpoint_should_accept_query_scraped_since_date(self, mock_gazette_interface, configure_app, client):
        interface = mock_gazette_interface()

        configure_app(gazettes=interface)

        response = client.get(
            "/gazettes",
            params={"territory_ids": "4205902","scraped_since": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")},
        )
        
        assert response.status_code == HTTPStatus.OK
        
    def test_gazettes_endpoint_should_accept_query_scraped_until_date(self, mock_gazette_interface, configure_app, client):
        interface = mock_gazette_interface()

        configure_app(gazettes=interface)

        response = client.get(
           "/gazettes",
            params={"territory_ids": "4205902","scraped_until": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")},
        )
        
        assert response.status_code == HTTPStatus.OK
        
    def test_gazettes_endpoint_should_fail_with_invalid_published_since_value(self, mock_gazette_interface, configure_app, client):
        interface = mock_gazette_interface()

        configure_app(gazettes=interface)
        
        response = client.get("/gazettes", params={"territory_ids": "4205902", "published_since": "foo-bar-2222"})

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_gazettes_endpoint_should_fail_with_invalid_published_until_value(self, mock_gazette_interface, configure_app, client):
        interface = mock_gazette_interface()

        configure_app(gazettes=interface)
        
        response = client.get("/gazettes", params={"territory_ids": "4205902", "published_until": "foo-bar-2222"})
        
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_gazettes_endpoint_should_fail_with_invalid_scraped_since_value(self, mock_gazette_interface, configure_app, client):
        interface = mock_gazette_interface()

        configure_app(gazettes=interface)
        
        response = client.get("/gazettes", params={"territory_ids": "4205902", "scraped_since": "foo-bar-2222"})

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_gazettes_endpoint_should_fail_with_invalid_scraped_until_value(self, mock_gazette_interface, configure_app, client):
        interface = mock_gazette_interface()

        configure_app(gazettes=interface)
        
        response = client.get("/gazettes", params={"territory_ids": "4205902", "scraped_until": "foo-bar-2222"})
        
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_gazettes_endpoint_should_fail_with_invalid_pagination_data(self, mock_gazette_interface, configure_app, client):
        interface = mock_gazette_interface()

        configure_app(gazettes=interface)
        
        response = client.get(
            "/gazettes", params={"territory_ids": "4205902", "offset": "asfasdasd", "size": "10"}
        )
        
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        
        response = client.get(
            "/gazettes", params={"territory_ids": "4205902", "offset": "10", "size": "ssddsfds"}
        )
        
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        
        response = client.get(
            "/gazettes", params={"territory_ids": "4205902", "offset": "x", "size": "asdasdas"}
        )
        
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_get_gazettes_without_territory_id_should_be_fine(self, mock_gazette_interface, configure_app, client):
        interface = mock_gazette_interface()

        configure_app(gazettes=interface)
        
        response = client.get("/gazettes")
        
        assert response.status_code == HTTPStatus.OK
        assert response.json() == {"total_gazettes": 0, "gazettes": []}
      
    def test_get_gazettes_should_request_gazettes_to_interface_object(self, mock_gazette_interface, configure_app, client):
        interface = mock_gazette_interface()

        configure_app(
            gazettes=interface
        )
        
        response = client.get("/gazettes", params={"territory_ids": "4205902"})
        
        assert response.status_code == HTTPStatus.OK
        interface.get_gazettes.assert_called_once()

    def test_get_gazettes_should_forward_gazettes_filters_to_interface_object(self, mock_gazette_interface, configure_app, client):
        interface = mock_gazette_interface()

        configure_app(
            gazettes=interface
        )

        today = date.today().isoformat()
        datetime_now = datetime.now().replace(microsecond=0).isoformat()
        
        response = client.get(
            "/gazettes",
            params={
                "territory_ids": "4205902",
                "published_since": today,
                "published_until": today,
                "scraped_since": datetime_now,
                "scraped_until": datetime_now,
                "querystring": "xpto",
                "excerpt_size": 500,
                "number_of_excerpts": 1,
                "pre_tags": ["<strong>"],
                "post_tags": ["</strong>"],
                "offset": 10,
                "size": 100,
                "sort_by": "relevance"
            },
        )
        
        assert response.status_code == HTTPStatus.OK
        interface.get_gazettes.assert_called_once()

        assert interface.get_gazettes.call_args.args[0].territory_ids[0] == "4205902"
        assert interface.get_gazettes.call_args.args[0].published_since == date.today()
        assert interface.get_gazettes.call_args.args[0].published_until == date.today()
        assert interface.get_gazettes.call_args.args[0].scraped_since == datetime.now().replace(microsecond=0)
        assert interface.get_gazettes.call_args.args[0].scraped_until == datetime.now().replace(microsecond=0)
        assert interface.get_gazettes.call_args.args[0].querystring == "xpto"
        assert interface.get_gazettes.call_args.args[0].excerpt_size == 500
        assert interface.get_gazettes.call_args.args[0].number_of_excerpts == 1
        assert interface.get_gazettes.call_args.args[0].pre_tags == ["<strong>"]
        assert interface.get_gazettes.call_args.args[0].post_tags == ["</strong>"]
        assert interface.get_gazettes.call_args.args[0].offset == 10
        assert interface.get_gazettes.call_args.args[0].size == 100
        assert interface.get_gazettes.call_args.args[0].sort_by == "relevance"
        
    def test_get_gazettes_should_return_json_with_items(self, mock_gazette_interface, configure_app, client):
        today = date.today()
        datetime_now = datetime.now().isoformat()
        
        interface = mock_gazette_interface(
            (
                1,
                [
                    {
                        "territory_id": "4205902",
                        "date": today,
                        "scraped_at": datetime_now,
                        "url": "https://queridodiario.ok.org.br/",
                        "territory_name": "My city",
                        "state_code": "My state",
                        "excerpts": [],
                        "edition": "12.3442",
                        "is_extra_edition": False,
                        "txt_url": "https://queridodiario.ok.org.br/123456/1a2345b678c9.txt",
                    }
                ],
            )
        )
        
        configure_app(
            gazettes=interface
        )
        
        response = client.get("/gazettes", params={"territory_ids": "4205902"})
        
        assert response.status_code == HTTPStatus.OK
        interface.get_gazettes.assert_called_once()
        
        assert interface.get_gazettes.call_args.args[0].territory_ids[0] == "4205902"
        
        assert response.json() == {
                "total_gazettes": 1,
                "gazettes": [
                    {
                        "territory_id": "4205902",
                        "date": today.strftime("%Y-%m-%d"),
                        "scraped_at": datetime_now,
                        "url": "https://queridodiario.ok.org.br/",
                        "territory_name": "My city",
                        "state_code": "My state",
                        "excerpts": [],
                        "edition": "12.3442",
                        "is_extra_edition": False,
                        "txt_url": "https://queridodiario.ok.org.br/123456/1a2345b678c9.txt",
                    }
                ],
            }

        
    def test_get_gazettes_should_return_empty_list_when_no_gazettes_is_found(self, mock_gazette_interface, configure_app, client):
        interface = mock_gazette_interface()

        configure_app(
            gazettes=interface
        )

        response = client.get("/gazettes", params={"territory_ids": "4205902"})
        
        interface.get_gazettes.assert_called_once()
        
        assert interface.get_gazettes.call_args.args[0].territory_ids[0] == "4205902"
        assert response.status_code == HTTPStatus.OK
        assert response.json() == {"total_gazettes": 0, "gazettes": []}
    

    def test_gazettes_endpoint_should_accept_query_querystring_date(self, mock_gazette_interface, configure_app, client):
        interface = mock_gazette_interface()

        configure_app(
            gazettes=interface
        )

        response = client.get(
            "/gazettes",
            params={"territory_ids": "4205902", "querystring": "keyword1 keyword2"}
        )
        
        interface.get_gazettes.assert_called_once()
        assert interface.get_gazettes.call_args.args[0].querystring == "keyword1 keyword2"

    def test_gazettes_endpoint_should_handle_array_querystring(self, mock_gazette_interface, configure_app, client):
        interface = mock_gazette_interface()

        configure_app(
            gazettes=interface
        )

        client.get(
            "/gazettes",
            params={"territory_ids": "4205902", "querystring": []}
        )
        
        interface.get_gazettes.assert_called_once()
        assert interface.get_gazettes.call_args.args[0].querystring == ""

    def test_get_gazettes_should_forward_querystring_to_interface_object(self, mock_gazette_interface, configure_app, client):
        interface = mock_gazette_interface()

        configure_app(
            gazettes=interface
        )

        client.get(
            "/gazettes",
            params={"territory_ids": "4205902", "querystring": "keyword1 1 True"}
        )

        interface.get_gazettes.assert_called_once()
        assert interface.get_gazettes.call_args.args[0].querystring == "keyword1 1 True"
        

    def test_get_gazettes_should_handle_none_querystring(self, mock_gazette_interface, configure_app, client):
        interface = mock_gazette_interface()

        configure_app(
            gazettes=interface
        )

        client.get(
            "/gazettes",
            params={"territory_ids": "4205902","querystring": None}
        )
        
        interface.get_gazettes.assert_called_once()
        assert interface.get_gazettes.call_args.args[0].querystring is not None

    def test_get_gazettes_should_handle_empty_querystring(self, mock_gazette_interface, configure_app, client):
        interface = mock_gazette_interface()

        configure_app(
            gazettes=interface
        )

        client.get(
            "/gazettes",
            params={"territory_ids": "4205902","querystring": ""}
        )
        
        interface.get_gazettes.assert_called_once()
        assert interface.get_gazettes.call_args.args[0].querystring == ""

    def test_gazettes_without_territory_ids_endpoint_should_accept_query_published_since_date(
            self,
            mock_gazette_interface,
            configure_app,
            client
        ):
        interface = mock_gazette_interface()

        configure_app(
            gazettes=interface
        )
        
        response = client.get(
            "/gazettes",
            params={"published_since": date.today().isoformat()}
        )
        
        assert response.status_code == HTTPStatus.OK

    def test_gazettes_without_territory_ids_endpoint_should_accept_query_published_until_date(self,
            mock_gazette_interface,
            configure_app,
            client
        ):
        interface = mock_gazette_interface()

        configure_app(
            gazettes=interface
        )
        
        response = client.get(
            "/gazettes", params={"published_until": date.today().isoformat()}
        )
        
        assert response.status_code == HTTPStatus.OK

    def test_gazettes_without_territory_ids_endpoint_should_accept_query_scraped_since_date(
            self,
            mock_gazette_interface,
            configure_app,
            client
        ):
        interface = mock_gazette_interface()

        configure_app(
            gazettes=interface
        )
        
        response = client.get(
            "/gazettes",
            params={"scraped_since": datetime.now().replace(microsecond=0).isoformat()}
        )
        
        assert response.status_code == HTTPStatus.OK

    def test_gazettes_without_territory_ids_endpoint_should_accept_query_scraped_until_date(
            self,
            mock_gazette_interface,
            configure_app,
            client
        ):
        interface = mock_gazette_interface()

        configure_app(
            gazettes=interface
        )
        
        response = client.get(
            "/gazettes", params={"scraped_until": datetime.now().replace(microsecond=0).isoformat()}
        )
        
        assert response.status_code == HTTPStatus.OK

    def test_gazettes_without_territory_ids_endpoint_should_fail_with_invalid_published_since_value(
            self,
            mock_gazette_interface,
            configure_app,
            client
        ):
        
        interface = mock_gazette_interface()

        configure_app(
            gazettes=interface
        )
        
        response = client.get("/gazettes", params={"published_since": "foo-bar-2222"})
        
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_gazettes_without_territory_endpoint_should_fail_with_invalid_published_until_value(
            self,
            mock_gazette_interface,
            configure_app,
            client
        ):
        
        interface = mock_gazette_interface()

        configure_app(
            gazettes=interface
        )
        
        response = client.get("/gazettes", params={"published_until": "foo-bar-2222"})
        
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_gazettes_without_territory_ids_endpoint_should_fail_with_invalid_scraped_since_value(
            self,
            mock_gazette_interface,
            configure_app,
            client
        ):
        
        interface = mock_gazette_interface()

        configure_app(
            gazettes=interface
        )
        
        response = client.get("/gazettes", params={"scraped_since": "foo-bar-2222"})
        
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_gazettes_without_territory_endpoint_should_fail_with_invalid_scraped_until_value(
            self,
            mock_gazette_interface,
            configure_app,
            client
        ):
        
        interface = mock_gazette_interface()

        configure_app(
            gazettes=interface
        )
        
        response = client.get("/gazettes", params={"scraped_until": "foo-bar-2222"})
        
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_get_gazettes_without_territory_id_should_forward_gazettes_filters_to_interface_object(
            self,
            mock_gazette_interface,
            configure_app,
            client
        ):
        
        interface = mock_gazette_interface()

        configure_app(
            gazettes=interface
        )
        response = client.get(
            "/gazettes",
            params={ #TODO: Ver se seria legal colocar os restos dos paramentros
                "published_since": date.today().isoformat(),
                "published_until": date.today().isoformat(),
                "offset": 10,
                "size": 100,
            },
        )
        assert response.status_code == HTTPStatus.OK
        interface.get_gazettes.assert_called_once()
        
        assert interface.get_gazettes.call_args.args[0].territory_ids is not None
        assert interface.get_gazettes.call_args.args[0].published_since == date.today()
        assert interface.get_gazettes.call_args.args[0].published_until == date.today()
        assert interface.get_gazettes.call_args.args[0].offset == 10
        assert interface.get_gazettes.call_args.args[0].size == 100

    def test_api_should_forward_the_result_offset(self, mock_gazette_interface, configure_app, client):
        interface = mock_gazette_interface()

        configure_app(
            gazettes=interface
        )
        
        response = client.get("/gazettes", params={"offset": 0})
        
        assert response.status_code == HTTPStatus.OK
        interface.get_gazettes.assert_called_once()
        assert interface.get_gazettes.call_args.args[0].offset == 0

    @pytest.mark.xfail
    def test_configure_api_should_failed_with_invalid_root_path(self, configure_app):
        configure_app(
            api_root_path=1,
        )

    def test_configure_api_root_path(self, configure_app):
        from api import app
        
        configure_app(
            api_root_path="/api/v1",
        )
        
        assert "/api/v1" == app.root_path

    def test_api_without_edition_and_extra_field(self, mock_gazette_interface, configure_app, client):
        today = date.today()
        yesterday = today - timedelta(days=1)

        datetime_now = datetime.now().replace(microsecond=0)
        yesterday_datetime_now = (datetime_now - timedelta(days=1))

        
        interface = mock_gazette_interface(
            (
                2,
                [
                    {
                        "territory_id": "4205902",
                        "date": today.isoformat(),
                        "scraped_at": datetime_now.isoformat(),
                        "url": "https://queridodiario.ok.org.br/",
                        "territory_name": "My city",
                        "state_code": "My state",
                        "excerpts": [],
                        "is_extra_edition": False,
                        "edition": "12.3442",
                        "txt_url": "https://queridodiario.ok.org.br/123/1a2345b678c9.txt",
                    },
                    {
                        "territory_id": "4205902",
                        "date": yesterday.isoformat(),
                        "scraped_at": yesterday_datetime_now.isoformat(),
                        "url": "https://queridodiario.ok.org.br/",
                        "territory_name": "My city",
                        "state_code": "My state",
                        "excerpts": [],
                        "is_extra_edition": False,
                        "edition": "12.3442",
                        "txt_url": "https://queridodiario.ok.org.br/456/1d2345e678f9.txt",
                    },

                ],
            )
        )
        
        configure_app(
            gazettes=interface, 
        )
        
        response = client.get("/gazettes", params={"territory_ids": "4205902"})
        
        interface.get_gazettes.assert_called_once()
        assert interface.get_gazettes.call_args.args[0].territory_ids[0] == "4205902"
        assert response.status_code == HTTPStatus.OK
        assert response.json() == {
                "total_gazettes": 2,
                "gazettes": [
                    {
                        "territory_id": "4205902",
                        "date": today.isoformat(),
                        "scraped_at": datetime_now.isoformat(),
                        "url": "https://queridodiario.ok.org.br/",
                        "territory_name": "My city",
                        "state_code": "My state",
                        "excerpts": [],
                        "is_extra_edition": False,
                        "edition": "12.3442",
                        "txt_url": "https://queridodiario.ok.org.br/123/1a2345b678c9.txt",
                    },
                    {
                        "territory_id": "4205902",
                        "date": yesterday.isoformat(),
                        "scraped_at": yesterday_datetime_now.isoformat(),
                        "url": "https://queridodiario.ok.org.br/",
                        "territory_name": "My city",
                        "state_code": "My state",
                        "excerpts": [],
                        "is_extra_edition": False,
                        "edition": "12.3442",
                        "txt_url": "https://queridodiario.ok.org.br/456/1d2345e678f9.txt",
                    },
                ],
            }

        
    def test_api_with_none_edition_and_extra_field(self, mock_gazette_interface, configure_app, client):
        today = date.today()
        yesterday = today - timedelta(days=1)

        datetime_now = datetime.now().replace(microsecond=0)
        yesterday_datetime_now = (datetime_now - timedelta(days=1))

        interface = mock_gazette_interface(
            (
                2,
                [
                    {
                        "territory_id": "4205902",
                        "date": today.isoformat(),
                        "scraped_at": datetime_now.isoformat(),
                        "url": "https://queridodiario.ok.org.br/",
                        "territory_name": "My city",
                        "state_code": "My state",
                        "excerpts": [],
                        "is_extra_edition": False,
                        "edition": "12.3442",
                        "txt_url": "https://queridodiario.ok.org.br/123/1a2345b678c9.txt",
                    },
                    {
                        "territory_id": "4205902",
                        "date": yesterday.isoformat(),
                        "scraped_at": yesterday_datetime_now.isoformat(),
                        "url": "https://queridodiario.ok.org.br/",
                        "territory_name": "My city",
                        "state_code": "My state",
                        "excerpts": [],
                        "is_extra_edition": None,
                        "edition": None,
                        "txt_url": "https://queridodiario.ok.org.br/456/1d2345e678f9.txt",
                    },
                ],
            )
        )
        
        configure_app(gazettes=interface)
        
        response = client.get("/gazettes", params={"territory_ids": "4205902"})
            
        interface.get_gazettes.assert_called_once()
        assert interface.get_gazettes.call_args.args[0].territory_ids[0] == "4205902"
        assert response.status_code == HTTPStatus.OK
        assert response.json() == {
                "total_gazettes": 2,
                "gazettes": [
                    {
                        "territory_id": "4205902",
                        "date": today.isoformat(),
                        "scraped_at": datetime_now.isoformat(),
                        "url": "https://queridodiario.ok.org.br/",
                        "territory_name": "My city",
                        "state_code": "My state",
                        "excerpts": [],
                        "is_extra_edition": False,
                        "edition": "12.3442",
                        "txt_url": "https://queridodiario.ok.org.br/123/1a2345b678c9.txt",
                    },
                    {
                        "territory_id": "4205902",
                        "date": yesterday.isoformat(),
                        "scraped_at": yesterday_datetime_now.isoformat(),
                        "url": "https://queridodiario.ok.org.br/",
                        "territory_name": "My city",
                        "state_code": "My state",
                        "excerpts": [],
                        "txt_url": "https://queridodiario.ok.org.br/456/1d2345e678f9.txt",
                    },
                ],
            }



class TestsApiCitiesEndpoint:
    def test_cities_endpoint_should_reject_request_without_partial_city_name(
            self,
            mock_city_interface,
            configure_app,
            client
        ):
        
        configure_app(
            cities=mock_city_interface()
        )
        
        response = client.get("/cities")
        
        assert response.status_code is not HTTPStatus.OK

    def test_cities_endpoint_should_accept_request_without_partial_city_name(
            self,
            mock_city_interface,
            configure_app,
            client
        ):
        
        configure_app(
            cities=mock_city_interface()
        )
        
        response = client.get("/cities", params={"city_name": "pirapo"})
        
        assert response.status_code == HTTPStatus.OK

    def test_cities_should_return_some_city_info(
            self,
            mock_city_interface,
            configure_app,
            client
        ):
        
        configure_app(
            cities=mock_city_interface()
        )
        
        response = client.get("/cities", params={"city_name": "pirapo"})
        
        assert response.status_code == HTTPStatus.OK
        assert response.json() == {"cities": []}
        

    def test_cities_should_request_data_from_city_interface(
            self,
            mock_city_interface,
            configure_app,
            client
        ):

        interface=mock_city_interface()
        configure_app(
            cities=interface
        )
        
        client.get("/cities", params={"city_name": "pirapo"})
        interface.get_cities.assert_called_once()


    def test_cities_should_return_data_returned_by_city_interface(
            self,
            mock_city_interface,
            configure_app,
            client
        ):

        today = date.today().isoformat()
        
        interface=mock_city_interface(
                cities_info=[
                    {
                        "territory_id": "2611606",
                        "territory_name": "Recife",
                        "state_code": "PE",
                        "publication_urls": ["https://querido-diario.org.br"],
                        "level": "1",
                        "availability_date": today
                    }
                ]
            )
        
        configure_app(cities=interface)
        
        response = client.get("/cities", params={"city_name": "Recife"})
        
        assert response.status_code == HTTPStatus.OK
        assert response.json() == {
                "cities": [
                    {
                        "territory_id": "2611606",
                        "territory_name": "Recife",
                        "state_code": "PE",
                        "publication_urls": ["https://querido-diario.org.br"],
                        "level": "1",
                        "availability_date": today
                    }
                ]
            }

    def test_city_endpoint_should_accept_request_with_city_id(
            self,
            mock_city_interface,
            configure_app,
            client
        ):

        today = date.today().isoformat()
        
        interface=mock_city_interface(
                city_info={
                        "territory_id": "2611606",
                        "territory_name": "Recife",
                        "state_code": "PE",
                        "publication_urls": ["https://querido-diario.org.br"],
                        "level": "1",
                        "availability_date": today
                   }
            )
        
        configure_app(cities=interface)

        response = client.get("/cities/2611606")
        assert response.status_code == HTTPStatus.OK

    def test_city_endpoint_should_return_404_with_city_id_not_found(
            self,
            mock_city_interface,
            configure_app,
            client
        ):
        
        configure_app(
            cities=mock_city_interface(),
        )
        response = client.get("/cities/1234")
        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_city_endpoint_should_request_data_from_city_interface(self, mock_city_interface, configure_app, client):
        today = date.today().isoformat()
        
        interface = mock_city_interface(
            city_info={
                "territory_id": "2611606",
                "territory_name": "Recife",
                "state_code": "PE",
                "publication_urls": ["https://querido-diario.org.br"],
                "level": "1",
                "availability_date": today
            }
        )
        
        configure_app(cities=interface)

        client.get("/cities/2611606")
        
        interface.get_city.assert_called_once()

    def test_city_endpoint_should_return_city_info_returned_by_city_interface(self, mock_city_interface, configure_app, client):
        today = date.today().isoformat()
        
        interface = mock_city_interface(
            city_info={
                "territory_id": "2611606",
                "territory_name": "Recife",
                "state_code": "PE",
                "publication_urls": ["https://querido-diario.org.br"],
                "level": "1",
                "availability_date": today
            }
        )

        configure_app(cities=interface)
        
        response = client.get("/cities/2611606")
        
        assert response.json() == {
                "city": {
                    "territory_id": "2611606",
                    "territory_name": "Recife",
                    "state_code": "PE",
                    "publication_urls": ["https://querido-diario.org.br"],
                    "level": "1",
                    "availability_date": today
                }
            }


        
class TestsApiSuggestionsEndpoint:


    def test_suggestion_endpoint_should_send_email(self, mock_suggestion_service_interface, configure_app, client):
        
        
        interface = mock_suggestion_service_interface(success=True, status="sent")

        configure_app(
            suggestion_service=interface
        )

        response = client.post(
            "/suggestions",
            json={
                "email_address": "some-email-from@email.com",
                "name": "My Name",
                "content": "Suggestion content",
            },
        )
        
        assert response.status_code == HTTPStatus.OK
        assert response.json() == {"status": "sent"}

    def test_api_should_fail_when_try_to_set_any_object_as_suggestions_service_interface(
        self,
        mocker,
        configure_app
    ):
        with pytest.raises(Exception):
            configure_app(
                suggestion_service=mocker.Mock(),
            )

    def test_suggestion_endpoint_should_fail_send_email(self, mock_suggestion_service_interface, configure_app, client):
        
        interface = mock_suggestion_service_interface(success=False, status="Could not sent message: an error")

        configure_app(
            suggestion_service=interface
        )
        

        response = client.post(
            "/suggestions",
            json={
                "email_address": "some-email-from@email.com",
                "name": "My Name",
                "content": "Suggestion content",
            },
        )
        
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.json() == {"status": "Could not sent message: an error"}


    def test_suggestion_endpoint_should_reject_when_email_address_is_not_present(self, mock_suggestion_service_interface, configure_app, client):

        configure_app(suggestion_service=mock_suggestion_service_interface())
        
        response = client.post(
            "/suggestions", json={"name": "My Name", "content": "Suggestion content",},
        )
        
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        assert response.json() == {
            "detail": [
                {
                    "loc": ["body", "email_address"],
                    "msg": "field required",
                    "type": "value_error.missing",
                }
            ]
        }

    def test_suggestion_endpoint_should_reject_when_name_is_not_present(self, mock_suggestion_service_interface, configure_app, client):

        configure_app(suggestion_service=mock_suggestion_service_interface())
        
        response = client.post(
            "/suggestions",
            json={
                "email_address": "some-email-from@email.com",
                "content": "Suggestion content",
            },
        )
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        assert response.json() == {
            "detail": [
                {
                    "loc": ["body", "name"],
                    "msg": "field required",
                    "type": "value_error.missing",
                }
            ]
        }

    def test_suggestion_endpoint_should_reject_when_content_is_not_present(self, mock_suggestion_service_interface, configure_app, client):

        configure_app(suggestion_service=mock_suggestion_service_interface())
        
        response = client.post(
            "/suggestions",
            json={"email_address": "some-email-from@email.com", "name": "My Name",},
        )
        
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        assert response.json() == {
            "detail": [
                {
                    "loc": ["body", "content"],
                    "msg": "field required",
                    "type": "value_error.missing",
                }
            ]
        }


