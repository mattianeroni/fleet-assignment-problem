
class Fleet {

    constructor ( attr ) {
        this.name = attr.name;
        this.cost = attr.cost;
        this.maxcap = attr.maxcap;
        this.mincap = attr.mincap;
        this.greencap = attr.greencap;
    }

}




module.exports = {
    Fleet
}