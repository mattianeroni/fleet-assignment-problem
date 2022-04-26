/*
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
This project concerns the development of a set of algorithms for solving the fleet 
assignment problem under additional constraints:
    - Limited capacity of fleets
    - Minimum load for fleets
    - Green capacity of fleets
    - Stochastic demand and stochastic productivity
    
This problem is completely new in scientific literature and the proposed solutions 
are supporteed and validated by a case study based on real data. 


Author: Mattia Neroni, Ph.D., Eng.
Contact: mneroni@uoc.edu
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
*/


const csv = require('convert-csv-to-json');
const fleet = require("./fleet.js")



class Problem {

    /*
        Initialise.

        :param avail: Available assignments.
        :param demand: The demand for each postcode.
        :param costs: The costs per parcel of vehicles.
        :param maxcap: The maximum capacities of vehicles.
        :param mincap: The minimum capacities of vehicles.
        :param greencap: The free capacity of vehicles that can be used without
                        involving any cost.
        :param prods: The productivity of each vehicle in each postcode.
        :param stdev: Possible deviations calculated on historical delays data.

    */
    constructor(attr) {
        this.avail = attr.avail;
        this.demand = attr.demand;
        this.costs = attr.costs;
        this.maxcap = attr.maxcap;
        this.mincap = attr.mincap;
        this.greencap = attr.greencap;
        this.prods = attr.prods;
        this.stdev = attr.stdev;
    }
}



/*
    Mathod used to read the case study problem.

    :param path: The directory where all the csv can be found.
    :param max_stdev: The maximum standard deviation on stochastic data (i.e., demand and productivity).
*/
function readproblem (path = "../data/", max_stdev=0.5) {

    // Init available assignments
    let availList = csv.fieldDelimiter(',').getJsonFromCsv(path + "FleetAreaConstraints.csv"); 
    let avail = {};

    // Demand
    let demandList = csv.fieldDelimiter(',').getJsonFromCsv(path + "Demand.csv"); 
    let demand = {};

    // Fleets characteristics 
    let fleetsList = csv.fieldDelimiter(',').getJsonFromCsv(path + "Fleets.csv"); 
    let fleetsObj = {};
    fleetsList.forEach( (i) => {
        let attr = i.Attr;
        delete i.Attr;
        fleetsObj[attr] = i;
    });
    let costs = fleetsObj.cost;
    let mincap = fleetsObj.mincapacity;
    let maxcap = fleetsObj.maxcapacity;
    let greencap = fleetsObj.greencapacity;
    for (let key of Object.keys(costs)){
        costs[key] = parseFloat(costs[key]);
        mincap[key] = parseInt(mincap[key]);
        maxcap[key] = parseInt(maxcap[key]);
        greencap[key] = parseInt(greencap[key]);
    }

    // Productivity
    let prodsList = csv.fieldDelimiter(',').getJsonFromCsv(path + "ParcelsPerH.csv"); 
    let prods = {};

    // St Dev 
    let stdevList = csv.fieldDelimiter(',').getJsonFromCsv(path + "Delayed.csv"); 
    let stdev = {};


    // Transform all lists in json object easier to handle
    for (let i = 0; i < availList.length; i++){
        let obj = availList[i];
        let postcode = parseInt(obj.Postcode);
        delete obj.Postcode;
        for (let [key, val] of Object.entries(obj)) 
            obj[key] = parseInt(val);
        avail[postcode] = obj;
        
        obj = demandList[i];
        postcode = parseInt(obj.Postcode);
        delete obj.Postcode;
        for (let [key, val] of Object.entries(obj)) 
            obj[key] = parseInt(val);
        demand[postcode] = obj;

        obj = prodsList[i];
        postcode = parseInt(obj.Postcode);
        delete obj.Postcode;
        for (let [key, val] of Object.entries(obj)) 
            obj[key] = parseFloat(val);
        prods[postcode] = obj;

        obj = stdevList[i];
        postcode = parseInt(obj.Postcode);
        delete obj.Postcode;
        for (let [key, val] of Object.entries(obj)) 
            obj[key] = parseFloat(val) * max_stdev;
        stdev[postcode] = obj;
    }
    
    return new Problem({avail, demand, costs, mincap, maxcap, greencap, prods, stdev});

}


module.exports = {
    readproblem,
}