base_x = 100;
base_y = 100;
base_z = 100;
thickness = 2;
spar_width = 10;

vent_x = base_x / 2 - 2 * thickness;
vent_y = base_y / 2 - 2 * thickness;




module square_vents() {

	translate([thickness,thickness,-5]) {
		cube([vent_x, vent_y, thickness]);
	}

	translate([base_x-thickness-vent_x,thickness,0]) {
		cube([vent_x, vent_y, thickness]);
	}

	translate([thickness,base_y-thickness-vent_y,0]) {
		cube([vent_x, vent_y, thickness]);
	}

	translate([base_x-thickness-vent_x,base_y-thickness-vent_y,0]) {
		cube([vent_x, vent_y, thickness]);
	}
}


module triangle_vents() {
	linear_extrude(height=thickness) {
		polygon(points=[[2*spar_width,spar_width],
						[base_x-2*spar_width,spar_width],
			    			[base_x/2,base_y/2-spar_width]], 
	    			paths=[[0,1,2]]);

		polygon(points=[[spar_width,2*spar_width],
						[spar_width,base_y-2*spar_width],
			    			[base_x/2-spar_width,base_y/2]], 
	    			paths=[[0,1,2]]);

		polygon(points=[[2*spar_width,base_y-spar_width],
						[base_x-2*spar_width,base_y-spar_width],
			    			[base_x/2,base_y/2+spar_width]], 
	    			paths=[[0,1,2]]);

		polygon(points=[[base_x-spar_width,base_y-2*spar_width],
						[base_x-spar_width,2*spar_width],
			    			[base_x/2+spar_width,base_y/2]], 
	    			paths=[[0,1,2]]);



	}
}



difference() {
	difference() {
		cube([base_x,base_y,base_z], center = false);;

		translate([thickness/2,thickness/2,thickness/2]) {
			cube([base_x - thickness, base_y - thickness,base_z - thickness], center=false);
		}

		triangle_vents();
		//square_vents();
	}

	translate([-10,-10,80]) {
		rotate([10,10,0]) {
			cube([150,150,100]);
		}
	}
}

translate([-10,-10,80]) {
	rotate([10,10,0]) {
		cube([150,150,10]);
	}
}
