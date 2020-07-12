from typing import Dict


def album_info_query(album_id: str) -> Dict:
  return {
    "id": 6,
    "operationName": "AlbumGet",
    "query": "query AlbumGet($id: ID!) {album {get(id: $id) {... on Album {...AlbumStandard} ... on MutationError "
             "{errors {code message}}}}} fragment AlbumStandard on Album "
             "{id title created_by number_of_pictures, number_of_animated_pictures}",
    "variables": {
      "id": album_id
    }
  }


def album_list_pictures_query(album_id: str, page_number: int) -> Dict:
  return {
    "id": 7,
    "operationName": "AlbumListOwnPictures",
    "query": "query AlbumListOwnPictures($input: PictureListInput!) {picture {list(input: $input) {info "
             "{...FacetCollectionInfo} items {...PictureStandardWithoutAlbum}}}} fragment FacetCollectionInfo on "
             "FacetCollectionInfo {page has_next_page has_previous_page total_items total_pages items_per_page } "
             "fragment PictureStandardWithoutAlbum on Picture {url_to_original url_to_video url}",
    "variables": {
      "input": {
        "filters": [{
          "name": "album_id",
          "value": album_id
        }],
        "display": "rating_all_time",
        "page": page_number
      }
    }
  }


def album_search_query(search_query: str, sorting: str = 'date_trending', page: int = 1) -> Dict:
  return {
    "id": 12,
    "operationName": "AlbumList",
    "query": "query AlbumList($input: AlbumListInput!) {album {list(input: $input) {info {...FacetCollectionInfo}"
             "items {...AlbumMinimal}}}}fragment FacetCollectionInfo on FacetCollectionInfo "
             "{page has_next_page has_previous_page total_items total_pages items_per_page}"
             "fragment AlbumMinimal on Album {__typename id title number_of_pictures number_of_animated_pictures "
             "created_by {id url name display_name user_title} }",
    "variables": {
      "input": {
        "display": sorting,
        "filters": [
          {
            "name": "album_type",
            "value": "pictures"
          },
          {
            "name": "search_query",
            "value": search_query
          }
        ],
        "page": page
      }
    }
  }


def user_albums_query(user_id: str, page_number: int) -> Dict:
  return {
    "id": 8,
    "operationName": "AlbumList",
    "query": "query AlbumList($input: AlbumListInput!) {album {list(input: $input) {"
             "info {...FacetCollectionInfo} items {...AlbumMinimal}}}}"
             "fragment FacetCollectionInfo on FacetCollectionInfo {"
             "page has_next_page has_previous_page total_items total_pages url_complete}"
             "fragment AlbumMinimal on Album {id}",
    "variables": {
      "input": {
        "display": "date_newest",
        "filters": [{
          "name": "created_by_id",
          "value": user_id
        }],
        "page": page_number
      }
    }
  }


def user_info_query(user_id: str) -> Dict:
  return {
    "id": 3, "operationName": "ProfileGet",
    "query": "query ProfileGet($user_id: ID!) {userprofile {get(user_id: $user_id) {... on UserProfile {id user {"
             "id name display_name user_title } "
             "number_of_posts number_of_albums number_of_videos is_banned"
             "filter_settings {uses_default_warnings audience_ids genres_blocked_ids genres_subscribed_ids} }"
             "... on MutationError {errors {code message}}}}}",
    "variables": {
      "user_id": user_id
    }
  }
