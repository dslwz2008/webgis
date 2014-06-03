var map;
var untiled;
var tiled;
// pink tile avoidance
OpenLayers.IMAGE_RELOAD_ATTEMPTS = 5;
// make OL compute scale according to WMS spec
OpenLayers.DOTS_PER_INCH = 25.4 / 0.28;

$('document').ready(function init(){
    //initialise file upload plugin
    uploadGPX();

    format = 'image/png';
    var bounds = new OpenLayers.Bounds(
        -180, -90,
        180, 90
    );
    var options = {
        controls: [],
        maxExtent: bounds,
        maxResolution: 1.40625,
        projection: "EPSG:4326",
        units: 'degrees'
    };
    map = new OpenLayers.Map('map', options);

    // setup tiled layer
    tiled = new OpenLayers.Layer.WMS(
        "world:TrueMarble - Tiled", "http://192.168.36.5:8080/geoserver/webgis/wms",
        {
            LAYERS: 'webgis:truemarble',
            STYLES: '',
            format: format,
            tiled: true,
            tilesOrigin : map.maxExtent.left + ',' + map.maxExtent.bottom
        },
        {
            buffer: 0,
            displayOutsideMaxExtent: true,
            isBaseLayer: true,
            yx : {'EPSG:4326' : true}
        }
    );

    // setup single tiled layer
    untiled = new OpenLayers.Layer.WMS(
        "world:TrueMarble - Untiled", "http://192.168.36.5:8080/geoserver/webgis/wms",
        {
            LAYERS: 'webgis:truemarble',
            STYLES: '',
            format: format
        },
        {
            singleTile: true,
            ratio: 1,
            isBaseLayer: true,
            yx : {'EPSG:4326' : true}
        }
    );

    var trkbounds = new OpenLayers.Bounds(
        80.0000762939453, 30,
        116, 34.25
    );
    var tracks = new OpenLayers.Layer.WMS(
        "webgis:tracks - Tiled", "http://192.168.36.5:8080/geoserver/webgis/wms",
        {
            LAYERS: 'webgis:tracks',
            STYLES: '',
            format: format,
            tiled: true,
            transparent: true,
            tilesOrigin : trkbounds.left + ',' + trkbounds.bottom
        },
        {
            buffer: 0,
            displayOutsideMaxExtent: false,
            isBaseLayer: false,
            yx : {'EPSG:4326' : true}
        }
    );

    map.addLayers([untiled, tiled, tracks]);

    //控件
    map.addControl(new OpenLayers.Control.PanZoomBar({
        position: new OpenLayers.Pixel(2, 15)
    }));
    map.addControl(new OpenLayers.Control.LayerSwitcher());
    map.addControl(new OpenLayers.Control.Navigation());
    map.addControl(new OpenLayers.Control.Scale(('scale')));
    map.addControl(new OpenLayers.Control.MousePosition({
        div: document.getElementById('location')
    }));
    map.zoomToExtent(trkbounds);

    // support GetFeatureInfo
    map.events.register('click', map, function (e) {
        document.getElementById('nodelist').innerHTML = "Loading... please wait...";
        var params = {
            REQUEST: "GetFeatureInfo",
            EXCEPTIONS: "application/vnd.ogc.se_xml",
            BBOX: map.getExtent().toBBOX(),
            SERVICE: "WMS",
            INFO_FORMAT: 'text/html',
            QUERY_LAYERS: tracks.params.LAYERS,
            FEATURE_COUNT: 50,
            Layers: 'postgis:tracks',
            WIDTH: map.size.w,
            HEIGHT: map.size.h,
            format: format,
            styles: tracks.params.STYLES,
            srs: tracks.params.SRS};

        // handle the wms 1.3 vs wms 1.1 madness
        if(map.layers[0].params.VERSION == "1.3.0") {
            params.version = "1.3.0";
            params.j = parseInt(e.xy.x);
            params.i = parseInt(e.xy.y);
        } else {
            params.version = "1.1.1";
            params.x = parseInt(e.xy.x);
            params.y = parseInt(e.xy.y);
        }

        //OpenLayers.loadURL("http://192.168.36.5:8080/geoserver/world/wms", params, this, setHTML, setHTML);
        var request = OpenLayers.Request.GET({
            url:"http://192.168.36.5:8080/geoserver/webgis/wms?",
            params: params,
            callback: setHTML
        });
        OpenLayers.Event.stop(e);
    });
});

// sets the HTML provided into the nodelist element
function setHTML(response){
    document.getElementById('nodelist').innerHTML = response.responseText;
}

function queryMapWithBounds(){
    var minlon = document.getElementById('minlon').value;
    var maxlon = document.getElementById('maxlon').value;
    var minlat = document.getElementById('minlat').value;
    var maxlat = document.getElementById('maxlat').value;
    if(minlon == "" || maxlon == "" || minlat == "" || maxlat == ""){
        alert("经纬度不能为空！");
        return;
    }
    if(minlon > 180.0 || minlon < -180.0 ||
        maxlon > 180.0 || maxlon < -180.0 ||
        minlat > 90.0 || minlat < -180.0 ||
        maxlat > 90.0 || maxlat < -90.0){
        alert("所填写经纬度已经超出范围！");
    }
    var bounds = new OpenLayers.Bounds(minlon, minlat, maxlon, maxlat);
    map.zoomToExtent(bounds);
}

function uploadGPX(){
    $('#gpxFile').fileupload({
        dataType: 'json',
        maxNumberOfFiles : 1,
        singleFileUploads:true,
        maxFileSize: 5000000,
        acceptFileTypes:  /\S+\.gpx$/i,
        autoUpload : true,
        replaceFileInput:false,
        forceIframeTransport:true,
        add: function(e, data){
            data.submit();
        },
        //上传完成后的回调
        done: function (e, data) {
            alert(data.result['status']);
        }
    });
}
