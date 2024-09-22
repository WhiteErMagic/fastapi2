import requests


response = requests.post('http://127.0.0.1:8080/advertisements/',
                                    json={
                                          'title': 'title222',
                                          'description': 'description1',
                                          'price': '123',
                                          'user': '1'
                                    })


response = requests.patch('http://127.0.0.1:8080/advertisements/1/',
                                    json={
                                          'description': 'description222',
                                    })


response = requests.get('http://127.0.0.1:8080/advertisements/1/')


response = requests.delete('http://127.0.0.1:8080/advertisements/1/')