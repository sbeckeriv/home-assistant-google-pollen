# Service Usage Examples

## Get Pollen Forecast Service

The `google_pollen.get_pollen_forecast` service allows you to query pollen data for any location. This is useful for creating automations based on your phone's GPS location.

## Basic Service Call

```yaml
service: google_pollen.get_pollen_forecast
data:
  latitude: 59.9139
  longitude: 10.7522
  language: en
  days: 3
```

## Automation Examples

### 1. Notification When Arriving at Work with High Pollen

```yaml
automation:
  - alias: "Pollen Alert at Work"
    trigger:
      - platform: zone
        entity_id: device_tracker.my_phone
        zone: zone.work
        event: enter
    action:
      - service: google_pollen.get_pollen_forecast
        data:
          latitude: "{{ state_attr('zone.work', 'latitude') }}"
          longitude: "{{ state_attr('zone.work', 'longitude') }}"
          days: 1
        response_variable: pollen_data
      - if:
          - condition: template
            value_template: >
              {% set grass = pollen_data.dailyInfo[0].pollenTypeInfo | selectattr('code', 'eq', 'GRASS') | first %}
              {{ grass.indexInfo.value | float > 3.0 }}
        then:
          - service: notify.mobile_app_my_phone
            data:
              title: "High Pollen at Work!"
              message: "Grass pollen level is high. Consider taking medication."
```

### 2. Pollen Alert Based on Current Phone Location

```yaml
automation:
  - alias: "Check Pollen at Current Location"
    trigger:
      - platform: time
        at: "07:00:00"
    condition:
      - condition: state
        entity_id: person.me
        state: "not_home"
    action:
      - service: google_pollen.get_pollen_forecast
        data:
          latitude: "{{ state_attr('device_tracker.my_phone', 'latitude') }}"
          longitude: "{{ state_attr('device_tracker.my_phone', 'longitude') }}"
          days: 1
        response_variable: pollen_data
      - service: notify.mobile_app_my_phone
        data:
          title: "Pollen Forecast"
          message: >
            {% set tree = pollen_data.dailyInfo[0].pollenTypeInfo | selectattr('code', 'eq', 'TREE') | first %}
            Tree pollen today: {{ tree.indexInfo.category }}
```

### 3. Compare Pollen Between Home and Vacation Location

```yaml
automation:
  - alias: "Vacation Pollen Check"
    trigger:
      - platform: zone
        entity_id: device_tracker.my_phone
        zone: zone.vacation_home
        event: enter
    action:
      - service: google_pollen.get_pollen_forecast
        data:
          latitude: "{{ state_attr('device_tracker.my_phone', 'latitude') }}"
          longitude: "{{ state_attr('device_tracker.my_phone', 'longitude') }}"
          days: 3
        response_variable: vacation_pollen
      - service: notify.mobile_app_my_phone
        data:
          title: "Vacation Pollen Forecast"
          message: >
            {% set grass = vacation_pollen.dailyInfo[0].pollenTypeInfo | selectattr('code', 'eq', 'GRASS') | first %}
            {% set tree = vacation_pollen.dailyInfo[0].pollenTypeInfo | selectattr('code', 'eq', 'TREE') | first %}
            Grass: {{ grass.indexInfo.category }}
            Tree: {{ tree.indexInfo.category }}
```

### 4. Daily Route Pollen Check

Check pollen along your daily commute route:

```yaml
automation:
  - alias: "Morning Commute Pollen Check"
    trigger:
      - platform: time
        at: "06:30:00"
    action:
      # Check pollen at home
      - service: google_pollen.get_pollen_forecast
        data:
          latitude: !secret home_latitude
          longitude: !secret home_longitude
          days: 1
        response_variable: home_pollen
      # Check pollen at work
      - service: google_pollen.get_pollen_forecast
        data:
          latitude: !secret work_latitude
          longitude: !secret work_longitude
          days: 1
        response_variable: work_pollen
      - service: notify.mobile_app_my_phone
        data:
          title: "Commute Pollen Report"
          message: >
            {% set home_grass = home_pollen.dailyInfo[0].pollenTypeInfo | selectattr('code', 'eq', 'GRASS') | first %}
            {% set work_grass = work_pollen.dailyInfo[0].pollenTypeInfo | selectattr('code', 'eq', 'GRASS') | first %}
            Home: {{ home_grass.indexInfo.category }}
            Work: {{ work_grass.indexInfo.category }}
```

## Response Data Format

The service returns data in this format:

```json
{
  "dailyInfo": [
    {
      "date": {
        "year": 2026,
        "month": 3,
        "day": 9
      },
      "pollenTypeInfo": [
        {
          "code": "GRASS",
          "displayName": "Grass",
          "inSeason": true,
          "indexInfo": {
            "category": "MODERATE",
            "indexDescription": "Moderate",
            "value": 3.2
          }
        }
      ],
      "plantInfo": [...]
    }
  ]
}
```

## Pollen Categories

- `NONE` - No pollen
- `VERY_LOW` - Very low levels
- `LOW` - Low levels  
- `MODERATE` - Moderate levels
- `HIGH` - High levels
- `VERY_HIGH` - Very high levels

## Pollen Types

### Categories
- `GRASS`
- `TREE`
- `WEED`

### Plant Types
- `ALDER`, `ASH`, `BIRCH`, `COTTONWOOD`, `CYPRESS_PINE`, `ELM`
- `GRAMINALES`, `HAZEL`, `JAPANESE_CEDAR`, `JUNIPER`, `MAPLE`
- `MUGWORT`, `OAK`, `OLIVE`, `PINE`, `RAGWEED`
