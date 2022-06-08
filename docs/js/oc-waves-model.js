/*
 * OcWavesModel
 *
 * Uses JS Class template:
 * https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Classes
**/
const OC_WAVES_MODEL_LOAD_EVENT = 'waveData:loaded'

class OcWavesModel {
  constructor(jsonData) {
    this.data = jsonData.data
    this.meta = jsonData.meta
    this.dateTime = luxon.DateTime
    this.triggerLoadEvent()
  }

  /*
   * Getters
  **/
  get waves() {
    return this.data
  }

  /*
   * Methods
  **/
  triggerLoadEvent() {
    console.log('trigger', OC_WAVES_MODEL_LOAD_EVENT, this)
    $(document).trigger(OC_WAVES_MODEL_LOAD_EVENT, [this] )
  }
}
