
Colors = {};
Colors.names = {
    aqua: "#00ffff",
    beige: "#f5f5dc",
    black: "#000000",
    blue: "#0000ff",
    brown: "#a52a2a",
    cyan: "#00ffff",
    darkblue: "#00008b",
    darkcyan: "#008b8b",
    darkgrey: "#a9a9a9",
    darkgreen: "#006400",
    darkkhaki: "#bdb76b",
    darkmagenta: "#8b008b",
    darkolivegreen: "#556b2f",
    darkorange: "#ff8c00",
    darkorchid: "#9932cc",
    darkred: "#8b0000",
    darksalmon: "#e9967a",
    darkviolet: "#9400d3",
    fuchsia: "#ff00ff",
    gold: "#ffd700",
    green: "#008000",
    indigo: "#4b0082",
    khaki: "#f0e68c",
    lightblue: "#add8e6",
    lightcyan: "#e0ffff",
    lightgreen: "#90ee90",
    lightgrey: "#d3d3d3",
    lightpink: "#ffb6c1",
    lightyellow: "#ffffe0",
    lime: "#00ff00",
    magenta: "#ff00ff",
    maroon: "#800000",
    navy: "#000080",
    olive: "#808000",
    orange: "#ffa500",
    pink: "#ffc0cb",
    purple: "#800080",
    violet: "#800080",
    red: "#ff0000",
    silver: "#c0c0c0",
    white: "#ffffff",
    yellow: "#ffff00"
};
function hexToRgb(hex) {
    var bigint = parseInt(hex, 16);
    var r = (bigint >> 16) & 255;
    var g = (bigint >> 8) & 255;
    var b = bigint & 255;

    return r + "," + g + "," + b;
}
function parse_string(string){
    shapes = []
    if(string!=""){
        var raw_shapes = string.split("|").map(s=>s.split(";").map(Number.parseFloat));
        if (typeof raw_shapes !== 'undefined'){
            raw_shapes.forEach((el)=>{
                shapes.push({x:el[0],y:el[1]});
            });
        }
    }
    return shapes
}
function draw(strings) {
    var shapes;
    var canvas = document.getElementById("canvas_loc");
    var ctx = canvas.getContext("2d");
    var color;
    strings.forEach((string, i)=>{
        shapes = parse_string(string);
        if(shapes.length ==0 ) return;
        ctx.beginPath();
        ctx.moveTo(shapes[0].x*canvas.width, shapes[0].y*canvas.height);
        for(var index=1; index<shapes.length;index++) {
            ctx.lineTo(shapes[index].x*canvas.width, shapes[index].y*canvas.height);
        }
        color = hexToRgb(Colors.names[Object.keys(Colors.names)[i]].slice(1));
        console.log("rgba("+color+", 0.5)")
        ctx.fillStyle = "rgba("+color+", 0.5)";
        ctx.fill();
        ctx.stroke();
        ctx.closePath();
    });
};

function draw_cameras(string) {
    var canvas = document.getElementById("canvas_loc");
    var ctx = canvas.getContext("2d");
    shapes = parse_string(string);
    for(var index=0; index<shapes.length;index++) {
        ctx.fillStyle= "rgba(0, 255,0, 0.7)";
        ctx.beginPath();
        ctx.arc(shapes[index].x*canvas.width,shapes[index].y*canvas.height,5,0,Math.PI*2);
        ctx.closePath();
        ctx.fill();
    }
}