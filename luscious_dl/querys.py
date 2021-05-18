def album_info_query(album_id: str) -> dict:
  """
  Build Album information query.
  :param album_id: Album id
  :return: Query
  """
  return {
    "operationName": "AlbumGet",
    "query": """query AlbumGet($id: ID!) {
                  album {
                    get(id: $id) {
                      ... on Album {...AlbumStandard}
                      ... on MutationError {errors {code message}}
                    }
                  }
                }
                fragment AlbumStandard on Album {
                  id
                  title
                  slug
                  url
                  description
                  created_by {
                    name
                    display_name
                  }
                  number_of_pictures
                  number_of_animated_pictures
                  language {
                    title
                  }
                  tags {
                    text
                  }
                  genres {
                    title
                  }
                  audiences {
                    title
                  }
                }
    """,
    "variables": {
      "id": album_id
    }
  }


def album_list_pictures_query(album_id: str, page_number: int) -> dict:
  """
  Build Album pictures query.
  :param album_id: Album id
  :param page_number: initial search page
  :return: Query
  """
  return {
    "operationName": "AlbumListOwnPictures",
    "query": """query AlbumListOwnPictures($input: PictureListInput!) {
                  picture {
                    list(input: $input) {
                      info {...FacetCollectionInfo}
                      items {...PictureStandardWithoutAlbum}
                    }
                  }
                }
                fragment FacetCollectionInfo on FacetCollectionInfo {
                  page
                  has_next_page
                  has_previous_page
                  total_items
                  total_pages
                  items_per_page
                }
                fragment PictureStandardWithoutAlbum on Picture {
                  url_to_original
                  url_to_video
                  url
                }
    """,
    "variables": {
      "input": {
        "filters": [
          {
            "name": "album_id",
            "value": album_id
          }
        ],
        "display": "rating_all_time",
        "page": page_number
      }
    }
  }


def album_search_query(search_query: str, sorting: str = 'date_trending', page: int = 1) -> dict:
  """
  Build Album search query.
  :param search_query: keyword
  :param sorting:
  :param page: initial search page
  :return: Query
  """
  return {
    "operationName": "AlbumList",
    "query": """query AlbumList($input: AlbumListInput!) {
                  album {
                    list(input: $input) {
                      info {...FacetCollectionInfo}
                      items {...AlbumMinimal}
                    }
                  }
                }
                fragment FacetCollectionInfo on FacetCollectionInfo {
                  page
                  has_next_page
                  has_previous_page
                  total_items
                  total_pages
                  items_per_page
                }
                fragment AlbumMinimal on Album {
                  __typename
                  id
                  title
                  number_of_pictures
                  number_of_animated_pictures
                  created_by {
                    id
                    url
                    name
                    display_name
                    user_title
                  }
                }
    """,
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


def user_albums_query(user_id: str, page_number: int) -> dict:
  """
  Build User albums query.
  :param user_id: User id
  :param page_number: page number
  :return: Query
  """
  return {
    "operationName": "AlbumList",
    "query": """query AlbumList($input: AlbumListInput!) {
                  album {
                    list(input: $input) {
                      info {...FacetCollectionInfo}
                      items {...AlbumMinimal}
                    }
                  }
                }
                fragment FacetCollectionInfo on FacetCollectionInfo {
                  page
                  has_next_page
                  has_previous_page
                  total_items
                  total_pages
                  url_complete
                }
                fragment AlbumMinimal on Album {
                  id
                }
    """,
    "variables": {
      "input": {
        "display": "date_newest",
        "filters": [
          {
            "name": "created_by_id",
            "value": user_id
          }
        ],
        "page": page_number
      }
    }
  }


def user_info_query(user_id: str) -> dict:
  """
  Build User information query.
  :param user_id: User id
  :return: Query
  """
  return {
    "operationName": "ProfileGet",
    "query": """query ProfileGet($user_id: ID!) {
                  userprofile {
                    get(user_id: $user_id) {
                      ... on UserProfile {
                        id 
                        user {
                          id
                          name
                          display_name
                          user_title
                        }
                        number_of_posts
                        number_of_albums
                        number_of_videos
                        number_of_favorite_albums
                        is_banned
                        filter_settings {
                          uses_default_warnings
                          audience_ids
                          genres_blocked_ids
                          genres_subscribed_ids
                        }
                      }
                      ... on MutationError {errors {code message}}
                    }
                  }
                }
    """,
    "variables": {
      "user_id": user_id
    }
  }


def user_favorites_query(user_id: str, page_number: int) -> dict:
  """
  Build User favorites query.
  :param user_id: User id
  :param page_number: page number
  :return: Query
  """
  return {
    "operationName": "AlbumList",
    "query": """query AlbumList($input: AlbumListInput!) {
                  album {
                    list(input: $input) {
                      info {
                        ...FacetCollectionInfo}items {...AlbumMinimal}
                      }
                    }
                  }
                  fragment FacetCollectionInfo on FacetCollectionInfo {
                    page
                    has_next_page
                    has_previous_page
                    total_items
                    total_pages
                    url_complete
                  }
                  fragment AlbumMinimal on Album {
                    id
                  }
    """,
    "variables": {
      "input": {
        "display": "date_newest",
        "filters": [
          {
            "name": "favorite_by_user_id",
            "value": user_id
          }
        ],
        "page": page_number
      }
    }
  }