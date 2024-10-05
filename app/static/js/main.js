async function verify_password(password) {
    return await fetch('/check_password', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            password: password,
        }),
    })
        .then(response => response.json())
        .then(data => {
            if (data['status'] === 200) {
                return data['token']
            } else {
                return false
            }
        })
        .catch((error) => {
            console.error('Error:', error);
        });
}

function generate_map(token) {
    // Get the values from the form fields
    let longitude = $('#longitude').val();
    let latitude = $('#latitude').val();
    let radius = $('#radius').val();
    let layers = $('#layers').val();
    let state = $('#state').val();


    // Convert the values to numbers
    longitude = Number(longitude);
    latitude = Number(latitude);
    radius = Number(radius);
    layers = Number(layers);
    state = String(state);

    // Initialize the map with the center set to the input coordinates
    mapboxgl.accessToken = token
    let map = new mapboxgl.Map({
        container: 'map',
        center: [longitude, latitude],
        zoom: 12,
    });
    let circle_size;

    map.on('load', function () {
        fetch('/calculate_coordinates', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                longitude: longitude,
                latitude: latitude,
                radius: radius,
                layers: layers,
                state: state,
            }),
        })
            .then(response => response.json())
            .then(data => {
                // Parse the data returned from the Flask route
                let geojson = {
                    type: 'FeatureCollection',
                    features: data.map(item => {
                        let [lat, lng, size] = item.split(',');
                        circle_size = Number(size);
                        return {
                            type: 'Feature',
                            geometry: {
                                type: 'Point',
                                coordinates: [Number(lng), Number(lat)]
                            },
                            properties: {
                                circle_size: Number(circle_size)
                            }
                        };
                    })
                };

                // Add a new source to the map
                map.addSource('circles', {
                    type: 'geojson',
                    data: geojson
                });

                // Add a new layer to the map
                map.addLayer({
                    id: 'circles',
                    type: 'circle',
                    source: 'circles',
                    paint: {
                        'circle-radius': {
                            stops: [
                                [0, 0],
                                [20, circle_size]
                            ],
                            base: 2
                        },
                        'circle-color': '#800080', // Change this to the color you want
                        'circle-opacity': 0.2 // Change this to the opacity you want
                    }
                });
            })
            .catch((error) => {
                console.error('Error:', error);
            });
    });
}

function generate_command() {
    let latitude = $('#latitude').val();
    let longitude = $('#longitude').val();
    let radius = $('#radius').val();
    let layers = $('#layers').val();
    let keywords = $('#keywords').val();
    let command = `python app/commands/find_places.py --location '${latitude}, ${longitude}' -r ${radius} --layers ${layers} -m -k '${keywords}'`;

    $('#command-text').text(command)
}

$(document).ready(function () {
    $('#loadMapButton').bind('click', async function () {
        let password = $('#password');
        let password_value = password.val();
        let token = await verify_password(password_value);

        if (token) {
            password.removeClass('border-error')
            generate_map(token);
        } else {
            password.addClass('border-error')
        }
    });

    $('#generateCommandButton').bind('click', function () {
        generate_command();
    });
});
