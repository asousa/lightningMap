var live = {};
live.target_div = 'livemap';
live.status_div = 'status';
live.ws_addr = "ws://llamas.stanford.edu:9000";
live.data = {};
live.data.raw = null;
live.data.last_req_time = null;

live.initialize = function() {
  // --------------- Initialize Base Tiles ---------------
  live.base_tile = L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {                      // OSM basic map
      maxZoom: 18,
      minZoom: 1,
      attribution: 'Map tiles by <a href="http://www.mapbox.com/m">Mapbox</a> Data by <a href="http://openstreetmap.org">OpenStreetMap</a>, under <a href="http://creativecommons.org/licenses/by-sa/3.0">CC BY SA</a>.'
  });

  // live.dark_tile = L.tileLayer('http://{s}.tiles.mapbox.com/v3/mapbox.control-room/{z}/{x}/{y}.png', {   // Dark map
  //     maxZoom: 18,
  //     minZoom: 1,
  //     attribution: 'Map tiles by <a href="http://www.mapbox.com/m">Mapbox</a> Data by <a href="http://openstreetmap.org">OpenStreetMap</a>, under <a href="http://creativecommons.org/licenses/by-sa/3.0">CC BY SA</a>.'
  // });

  // live.toner_tile = L.tileLayer('http://{s}.tile.stamen.com/toner/{z}/{x}/{y}.jpg', {                     // Highest Contrast
  //     maxZoom: 18,
  //     minZoom: 1,
  //     attribution: 'Map tiles by <a href="http://www.mapbox.com/m">Mapbox</a> Data by <a href="http://openstreetmap.org">OpenStreetMap</a>, under <a href="http://creativecommons.org/licenses/by-sa/3.0">CC BY SA</a>.'
  // });

  live.baseLayer = {
    "Light": live.base_tile
    // "Dark": live.dark_tile,
    // "Xerox": live.toner_tile
  };

  // ------------ Initialize Content Layers ------------
  // Layer Groups
  live.gld_group = new L.LayerGroup();
  live.nldn_group =  new L.LayerGroup();
  live.sat_group =  new L.LayerGroup();
  live.daynite = new L.LayerGroup();
  live.box_group =  new L.LayerGroup();

  // Current layers
  live.flash_layer = L.geoJson();
  live.nldn_layer = L.geoJson();
  live.sat_layer = L.geoJson();
  live.box_layer = L.geoJson();
  live.term = L.terminator();

  live.term.addTo(live.daynite);


  live.layer_list = {
    "Lightning (GLD)": live.gld_group,
    "Lightning (NLDN)": live.nldn_group,
    "Satellites": live.sat_group,
    "Day/Night": live.daynite,
    "Bounding Boxes": live.box_group,
  };
    /*
    Bounding box.
    */
  live.southWest = L.latLng(-90, -180);
  live.northEast = L.latLng(90, 180);
  live.bounds = L.latLngBounds(live.southWest, live.northEast);

  // Create map, add layers ---------------------
  live.map = L.map(live.target_div, {
                                     center:[0, 0],
                                     zoom: 3,
                                     maxBounds: live.bounds,
                                     layers: [live.base_tile, live.gld_group, live.nldn_group,
                                      live.sat_group, live.daynite, live.box_group]
                                   });

  // keep us centered on a single copy
  live.map.worldCopyJump = true;
  L.control.layers(live.baseLayer, live.layer_list).addTo(live.map);


  live.total_sats = 0;
  live.total_boxes = 0;
  live.total_gld = 0;
  live.total_nldn = 0;


  // live.data.GLD = [];
  // live.data.NLDN = [];
  // live.data.sats = [];
  // live.data.boxes = [];

}


// Pictures instead of markers for satellites
live.sat_icon = L.icon({
    iconUrl: 'FP_Satellite_icon.svg',
    //iconUrl: 'moltres2.png',
    //iconSize: [48,48]
    iconSize: [24,24],
 });



// ------------------------------------------------------------------------
//      Marker adders (here for neatness)
// ------------------------------------------------------------------------
// --------- GLD ----------
live.addGLD = function() {
  live.total_gld = 0;
  
  live.flash_layer.removeEventListener();
  live.flash_layer.unbindPopup;
  live.map.removeLayer(live.flash_layer);
//  live.map.removeLayer(live.gld_group.getLayers());
//  live.flash_layer.removeLayer(live.map);

  live.flash_layer = null;
  live.flash_layer = L.geoJson(live.data.raw,{
      filter: function(feature) {
              var filt = (feature.name == "GLD");
              if (filt) { live.total_gld += 1;}
        return filt},

      onEachFeature: function (feature, layer) {
        var popupOptions = {maxWidth: 500};
        layer.bindPopup("<b>Time: </b>" + feature.time + "<br>" +
                        "<b>Location:</b> "+ feature.geometry.coordinates + "<br>" +
                        "<b>Peak Current:</b>" + feature.kA,popupOptions);
    },
      
      pointToLayer: function (feature, latlng) {
          var circles = L.circleMarker(latlng, {
          radius: feature.radius,
          fillColor: "#ff7800",
          color: "#000",
          weight: 0.5,
          opacity: 0.6,
          fillOpacity: 0.6
        });
          return circles;
      }
    }).addTo(live.gld_group);
}

// --------- NLDN ----------
live.addNLDN = function() {
  live.total_nldn = 0;
  live.nldn_layer.removeEventListener();
  live.nldn_layer.unbindPopup;
  live.map.removeLayer(live.nldn_layer);
  //live.map.removeLayer(live.nldn_group.getLayers());

//  live.nldn_layer.removeLayer(live.map);
  live.nldn_layer = null;
  live.nldn_layer = L.geoJson(live.data.raw,{
      filter: function(feature) {
              var filt = (feature.name == "NLDN");
              if (filt) { live.total_nldn += 1;}
        return filt},

      onEachFeature: function (feature, layer) {
        var popupOptions = {maxWidth: 500};
        layer.bindPopup("<b>Time: </b>" + feature.time + "<br>" +
                        "<b>Location:</b> "+ feature.geometry.coordinates + "<br>" +
                        "<b>Peak Current:</b>" + feature.kA,popupOptions);
    },
      
      pointToLayer: function (feature, latlng) {
          var circles = L.circleMarker(latlng, {
          radius: feature.radius,
          fillColor: "#ffff00",
          color: "#000",
          weight: 0.5,
          opacity: 0.6,
          fillOpacity: 0.6
        });
          return circles;
      }
    }).addTo(live.nldn_group);
}

// ---------- Sats ------------
live.addSats = function () {
  live.total_sats = 0;
  live.sat_layer.removeEventListener();
  live.sat_layer.unbindPopup;
  live.map.removeLayer(live.sat_layer);
  //live.map.removeLayer(live.sat_group.getLayers());

//  live.sat_layer.removeLayer(live.map);
  live.sat_layer = null;
  live.sat_layer = L.geoJson(live.data.raw,{
      filter: function(feature) {
              var filt = (feature.name == "Satellite");
              if (filt) { live.total_sats += 1;}
        return filt},

      onEachFeature: function (feature, layer) {
        var popupOptions = {maxWidth: 500};
        layer.bindPopup("<b>Name: </b> " + feature.satname + "<br><b>Time: </b>" + feature.time + "<br><b>Location:</b> "+ feature.geometry.coordinates,popupOptions);
    },
      
      pointToLayer: function (feature, latlng) {
        var satmarks = L.marker(latlng, {
          title: "Satellite",
          icon: live.sat_icon
        });
       return satmarks;
      }
      }).addTo(live.sat_group);
}

// --------- Add Bounding Boxes -----------
live.addBoxes = function () {
  live.total_boxes = 0;
  live.box_layer.removeEventListener();
  live.box_layer.unbindPopup;
  live.map.removeLayer(live.box_layer);
  //live.map.removeLayer(live.box_group.getLayers());

//  live.box_layer.removeLayer(live.map);


  live.box_layer = null;
  live.box_layer = L.geoJson(live.data.raw,{
    filter: function(feature) {
        var filt = (feature.name == "box");
        if (filt) { live.total_boxes += 1;}
      return filt},

     onEachFeature: function (feature, layer) {
       var popupOptions = {maxWidth: 500};
       layer.bindPopup("<b>Total Counts: </b>" + feature.properties.counts,popupOptions);
     },

     style: function(feature) {
        var feet = {
         fillColor: "#0088ff",
         color: "#000",
         weight: 0.5,
         opacity: 0.4,
         fillOpacity: 0.2};
         return feet}
     }).addTo(live.box_group);
}

live.updateTerminator = function () {
  var t2 = L.terminator({time: live.data.last_req_time});
  live.term.setLatLngs(t2.getLatLngs());
  live.term.redraw();
}


// ------------------------------------------------------------------------
//      Main update function -- Runs each time new data is received:
// ------------------------------------------------------------------------
live.update_map = function() {
  //console.log('Pulled fresh points')
  //console.log(this.resp)

  live.addBoxes();
  live.addNLDN();
  live.addGLD();
  live.addSats();
  live.updateTerminator();

  // // disp_status(Object.keys(resp).length + " entries")
//  live.disp_status((live.data.GLD.length/60.0).toPrecision(3) + " flashes / min")
  live.disp_status((live.total_gld/60.0).toPrecision(3) + " flashes / min")

  //console.log("Total GLD: " + live.total_gld);
  //console.log("Total Sats: " + live.total_sats);
  
};


// ------------------------------------------------------------------------
//     Receive new entries, sort into appropriate lists:
// ------------------------------------------------------------------------
live.data.load = function(msg) {
  // live.data.GLD = [];
  // live.data.NLDN = [];
  // live.data.sats = [];
  // live.data.boxes = [];
  // // // console.log(msg);
  // // for (var m in msg) {
  // //   if (msg[m].name == "GLD") {    
  // //       live.data.GLD.push(msg[m]);
  // //   } else if (msg[m].name == 'NLDN') {
  // //       live.data.NLDN.push(msg[m]);
  // //   } else if (msg[m].name == 'Satellite') {
  // //       live.data.sats.push(msg[m]);
  // //   } else if (msg[m].name == 'box') {
  // //       live.data.boxes.push(msg[m]);
  // //   }
  // // }

  live.data.raw = null;
  // console.log(live.total_gld);
  // console.log(live.total_sats);
  // console.log(live.total_boxes);
  live.data.raw = msg;
}

// Display status messages
live.disp_status = function(msg) {
  document.getElementById(live.status_div).innerHTML = msg;
};


// ----------------- WebSocket stuff: -------------------

live.ws = new WebSocket(live.ws_addr);
live.ws.binaryType = "arraybuffer";


live.ws.onopen = function() {
  live.disp_status('Connected');
  //console.log('Connected!');
}

live.ws.onmessage = function(event) {
  //console.log("message received: ");
  live.disp_status("message received: ");
  var msg = JSON.parse(event.data);
  live.data.load(msg); 
  live.update_map();
  msg = null; 
  }

live.ws.onclose = function() {
  live.disp_status('Connection closed');
}
live.ws.request_update = function(time) {
  live.data.last_req_time = time;
  //console.log(live.data.last_req_time)
  live.ws.send(live.data.last_req_time);
}