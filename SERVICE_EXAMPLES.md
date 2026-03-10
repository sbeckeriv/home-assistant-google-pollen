# Service Usage Examples

## Get Pollen Forecast Service

The `google_pollen.get_pollen_forecast` service allows you to query pollen data for any location. This is useful for creating automations based on your phone's GPS location.

## Using the Service in Automations

After adding the integration, you'll find the service under "Google pollen: Get pollen forecast" in the automation action selector.

### In the Home Assistant UI:
1. Go to **Settings** → **Automations & Scenes** → **Create Automation**
2. Add an action → **Call service**
3. Search for "**Google pollen: Get pollen forecast**"
4. Fill in the fields:
   - **Latitude**: Decimal latitude (-90 to 90)
   - **Longitude**: Decimal longitude (-180 to 180)
   - **Language**: Language code (default: en)
   - **Days**: Number of forecast days (1-5, default: 1)
5. Enable "**Response data**" and set a variable name (e.g., `pollen_data`)

## Basic Service Call (YAML)

```yaml
service: google_pollen.get_pollen_forecast
data:
  latitude: 59.9139
  longitude: 10.7522
  language: en
  days: 3
response_variable: pollen_data
```

## Simple Test Automation

Here's a minimal automation you can paste into the UI to test the service:

```yaml
alias: "Test Pollen Service"
description: Test the pollen forecast service
triggers:
  - trigger: state
    entity_id:
      - input_button.test_pollen
conditions: []
actions:
  - action: google_pollen.get_pollen_forecast
    data:
      latitude: 59.9139
      longitude: 10.7522
      days: 1
    response_variable: pollen_data
  - action: persistent_notification.create
    data:
      title: "Pollen Data Retrieved"
      message: "{{ pollen_data }}"
mode: single
```

**To test without a button trigger**: Change the trigger to `- trigger: time` with `at: "12:00:00"` or use Developer Tools → Services to call it manually.

## Automation Examples

### 1. Notification When Arriving at Work with High Pollen

```yaml
alias: "Pollen Alert at Work"
description: Notify when grass pollen is high at work location
triggers:
  - trigger: zone
    entity_id: device_tracker.my_phone
    zone: zone.work
    event: enter
conditions: []
actions:
  - action: google_pollen.get_pollen_forecast
    data:
      latitude: "{{ state_attr('zone.work', 'latitude') }}"
      longitude: "{{ state_attr('zone.work', 'longitude') }}"
      days: 1
    response_variable: pollen_data
  - condition: template
    value_template: >
      {% set grass_list = pollen_data.get('dailyInfo', [{}])[0].get('pollenTypeInfo', []) | selectattr('code', 'eq', 'GRASS') | list %}
      {{ grass_list | length > 0 and grass_list[0].get('indexInfo', {}).get('value', 0) | float > 3.0 }}
  - action: notify.mobile_app_my_phone
    data:
      title: "High Pollen at Work!"
      message: "Grass pollen level is high. Consider taking medication."
mode: single
```

### 2. Pollen Alert Based on Current Phone Location

```yaml
alias: "Check Pollen at Current Location"
description: Send daily pollen report based on phone location
triggers:
  - trigger: time
    at: "07:00:00"
conditions:
  - condition: state
    entity_id: person.me
    state: "not_home"
actions:
  - action: google_pollen.get_pollen_forecast
    data:
      latitude: "{{ state_attr('device_tracker.my_phone', 'latitude') }}"
      longitude: "{{ state_attr('device_tracker.my_phone', 'longitude') }}"
      days: 1
    response_variable: pollen_data
  - action: notify.mobile_app_my_phone
    data:
      title: "Pollen Forecast"
      message: >
        {% set tree_list = pollen_data.get('dailyInfo', [{}])[0].get('pollenTypeInfo', []) | selectattr('code', 'eq', 'TREE') | list %}
        {% if tree_list | length > 0 %}
        Tree pollen today: {{ tree_list[0].get('indexInfo', {}).get('category', 'Unknown') }}
        {% else %}
        Tree pollen data not available
        {% endif %}
mode: single
```

### 3. Vacation Pollen Check

```yaml
alias: "Vacation Pollen Check"
description: Get pollen forecast when arriving at vacation location
triggers:
  - trigger: zone
    entity_id: device_tracker.my_phone
    zone: zone.vacation_home
    event: enter
conditions: []
actions:
  - action: google_pollen.get_pollen_forecast
    data:
      latitude: "{{ state_attr('device_tracker.my_phone', 'latitude') }}"
      longitude: "{{ state_attr('device_tracker.my_phone', 'longitude') }}"
      days: 3
    response_variable: vacation_pollen
  - action: notify.mobile_app_my_phone
    data:
      title: "Vacation Pollen Forecast"
      message: >
        {% set daily = vacation_pollen.get('dailyInfo', [{}])[0] %}
        {% set pollen_types = daily.get('pollenTypeInfo', []) %}
        {% set grass_list = pollen_types | selectattr('code', 'eq', 'GRASS') | list %}
        {% set tree_list = pollen_types | selectattr('code', 'eq', 'TREE') | list %}
        Grass: {{ grass_list[0].get('indexInfo', {}).get('category', 'N/A') if grass_list | length > 0 else 'N/A' }}
        Tree: {{ tree_list[0].get('indexInfo', {}).get('category', 'N/A') if tree_list | length > 0 else 'N/A' }}
mode: single
```

### 4. Daily Commute Pollen Check

Check pollen at home and work locations:

```yaml
alias: "Morning Commute Pollen Check"
description: Compare pollen levels between home and work
triggers:
  - trigger: time
    at: "06:30:00"
conditions: []
actions:
  - action: google_pollen.get_pollen_forecast
    data:
      latitude: !secret home_latitude
      longitude: !secret home_longitude
      days: 1
    response_variable: home_pollen
  - action: google_pollen.get_pollen_forecast
    data:
      latitude: !secret work_latitude
      longitude: !secret work_longitude
      days: 1
    response_variable: work_pollen
  - action: notify.mobile_app_my_phone
    data:
      title: "Commute Pollen Report"
      message: >
        {% set home_grass = home_pollen.get('dailyInfo', [{}])[0].get('pollenTypeInfo', []) | selectattr('code', 'eq', 'GRASS') | list %}
        {% set work_grass = work_pollen.get('dailyInfo', [{}])[0].get('pollenTypeInfo', []) | selectattr('code', 'eq', 'GRASS') | list %}
        Home: {{ home_grass[0].get('indexInfo', {}).get('category', 'N/A') if home_grass | length > 0 else 'N/A' }}
        Work: {{ work_grass[0].get('indexInfo', {}).get('category', 'N/A') if work_grass | length > 0 else 'N/A' }}
mode: single
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
