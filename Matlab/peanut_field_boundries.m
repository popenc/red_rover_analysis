% peanut_field = gpxread('/home/brad/Desktop/peanut_field_latlon_only_fixed.gpx');
peanut_field = gpxread('/home/brad/Desktop/gpx_output.gpx');

states = geoshape(shaperead('usastatehi', 'UseGeoCoords', true));

placenames = gpxread('boston_placenames');
route = gpxread('sample_route.gpx');

stateName = 'Massachusetts';
ma = states(strcmp(states.Name, stateName));

figure
% ax = usamap('conus');
% oceanColor = [.5 .7 .9];
% setm(ax, 'FFaceColor', oceanColor)
% geoshow(states)
geoshow(peanut_field)
title({ ...
    'Conterminous USA State Boundaries', ...
    'Polygon Geographic Vector Data'})

% figure
% ax = usamap('ma');
% setm(ax, 'FFaceColor', oceanColor)
% geoshow(states)
% geoshow(ma, 'LineWidth', 1.5, 'FaceColor', [.5 .8 .6])
% geoshow(placenames);
% geoshow(route.Latitude, route.Longitude);
% title({'Massachusetts and Surrounding Region', 'Placenames and Route'})