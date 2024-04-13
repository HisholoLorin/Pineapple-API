from routers.sensor.pyeto import convert, fao
from datetime import datetime
from .WaterPrediction import WaterPrediction


def latitudeDegree(degree, minute, second):
    second = second / 60
    minute = minute + second
    return degree + (minute / 60)


def cropEvapotranspiration(ETo):
    kc = 0.3  # Pineapple coefficient at the later stage
    ETc = ETo * kc
    return round(ETc, 3)


def currentYear():
    return datetime.now().strftime("%Y")


def waterRequirement(ETc):
    r = 30
    e = 0.4  # Efficiency of irrigation system ie e = 40%
    # Volume of wager applied per plant
    volume = (ETc / 10) * ((r ** 2) / e)  # In millilitres
    return round(volume, 0)


def calculateWaterRequirement(db):
    morning = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    night = morning.replace(hour=23, minute=59, second=59, microsecond=0)
    aggregation = [{"$match": {"createdAt": {"$gte": morning, "$lte": night}}},
                   {"$project": {
                       "_id": 0,
                       "minTemp": {"$min": "$temperature"},
                       "maxTemp": {"$max": "$temperature"},
                       "minRelativeHumidity": {"$min": "$humidity"},
                       "maxRelativeHumidity": {"$max": "$humidity"},
                       "soilMoisture": {"$round": {"$avg": "$soilMoisture"}},
                       "solarRadiation": {"$round": [{"$avg": "$solarRadiation"}, 2]}
                   }}]
    data = db.sensor.aggregate(aggregation)
    result = list(data)[0]

    minTemp = result["minTemp"]
    maxTemp = result["maxTemp"]
    minRelativeHumidity = result["minRelativeHumidity"]
    maxRelativeHumidity = result["maxRelativeHumidity"]
    soilMoisture = result["soilMoisture"]
    solarRadiation = result["solarRadiation"]

    WaterPredictionObject = WaterPrediction()
    waterRequirementPrediction = WaterPredictionObject.predict(solarRadiation, maxTemp)

    dayOfYear = int(datetime.now().strftime("%j"))
    ETo = referenceEvapotranspiration(minTemp, maxTemp, minRelativeHumidity, maxRelativeHumidity,
                                      solarRadiation, dayOfYear)
    ETc = cropEvapotranspiration(ETo)
    waterRequirement(ETc=ETc)

    data = {
        "minTemperature": minTemp, "maxTemperature": maxTemp,
        "minRelativeHumidity": minRelativeHumidity, "maxRelativeHumidity": maxRelativeHumidity,
        "soilMoisture": soilMoisture, "solarRadiation": solarRadiation,
        "ETo": ETc, "ETc": ETc, "waterRequirement": waterRequirement(ETc=ETc),
        "waterRequirementPrediction": waterRequirementPrediction,
        "createdAt": datetime.now(),
        "updatedAt": datetime.now()
    }
    db.result.update_one({"createdAt": {"$gte": morning, "$lte": night}}, {"$set": data}, upsert=True)


def referenceEvapotranspiration(minTemp, maxTemp, minRelativeHumidity, maxRelativeHumidity,
                                solarRadiation, dayOfYear, windSpeed=3.82):
    # Air Temperature
    temperature = (minTemp + maxTemp) / 2  # Celsius (C)

    # WindSpeed at 2m
    windSpeedAt2m = fao.wind_speed_2m(windSpeed, 2)  # Wind speed at 2 m above the surface [m s-1]

    # Saturation Vapor Pressure
    saturationVaporPressure = fao.svp_from_t(temperature)  # Saturation vapour pressure [kPa]

    # Actual Vapor Pressure
    actualVaporPressure = fao.avp_from_rhmin_rhmax(fao.svp_from_t(minTemp),
                                                   fao.svp_from_t(maxTemp),
                                                   minRelativeHumidity,
                                                   maxRelativeHumidity)  # Actual vapour pressure [kPa]

    # Slope of the saturation vapour pressure curve
    deltaSaturationVaporPressure = fao.delta_svp(temperature)

    atmosphericPressure = fao.atm_pressure(504.47)  # atmospheric pressure [kPa]
    pyschrometricConstant = fao.psy_const(atmosphericPressure)  # Psychrometric constant [kPa degC-1]

    # solarRadiation = 25 # megajoules per square meter per day (MJ m-2 day-1)
    netIncomingShortWaveRadiation = fao.net_in_sol_rad(
        solarRadiation)  # Net incoming solar (or shortwave) radiation [MJ m-2 day-1]

    # Chumukedima - Latitude: 25° 47' 29.76" N Longitude: 93° 46' 54.48" E
    # Medziphema - latitude : 25° 46' 39.2916" N Longitude: 93° 55' 35.5224"

    latitude = convert.deg2rad(latitudeDegree(25, 46, 39.2916))
    solarDeclination = fao.sol_dec(dayOfYear)

    extraterrestrialRadiation = fao.et_rad(latitude, solarDeclination,
                                           fao.sunset_hour_angle(latitude, solarDeclination),
                                           fao.inv_rel_dist_earth_sun(
                                               dayOfYear))  # Daily extraterrestrial radiation [MJ m-2 day-1]
    clearSkySolarRadiation = fao.cs_rad(0, extraterrestrialRadiation)  # Clear sky radiation [MJ m-2 day-1]
    netOutgoingLongWaveRadiation = fao.net_out_lw_rad(minTemp, maxTemp, solarRadiation, clearSkySolarRadiation,
                                                      actualVaporPressure)  # Net outgoing longwave radiation [MJ m-2 day-1]

    # Net Radiation
    netRadiation = fao.net_rad(netIncomingShortWaveRadiation, netOutgoingLongWaveRadiation)

    ETo = fao.fao56_penman_monteith(netRadiation, temperature, windSpeedAt2m, saturationVaporPressure,
                                    actualVaporPressure, deltaSaturationVaporPressure, pyschrometricConstant)
    # Reference evapotranspiration (ETo) from a hypotheticalgrass reference surface [mm day-1]
    return round(ETo, 3)
