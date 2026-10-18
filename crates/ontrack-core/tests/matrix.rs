use ontrack_core::geocoder::Location;
use ontrack_core::matrix::{build_distance_matrix, haversine, Backend};

fn loc(name: &str, lat: f64, lng: f64) -> Location {
    Location {
        address: name.into(),
        lat: Some(lat),
        lng: Some(lng),
    }
}

fn unresolved(name: &str) -> Location {
    Location {
        address: name.into(),
        lat: None,
        lng: None,
    }
}

#[test]
fn haversine_same_point_is_zero() {
    assert_eq!(haversine(47.6, -117.4, 47.6, -117.4), 0.0);
}

#[test]
fn haversine_spokane_to_seattle() {
    // Great-circle distance is ~368 km (the ~449 km figure is by road).
    let d = haversine(47.6587, -117.4260, 47.6062, -122.3321);
    assert!((d - 368_000.0).abs() < 12_000.0, "got {d}");
}

#[test]
fn haversine_antipodal_is_half_circumference() {
    let d = haversine(0.0, 0.0, 0.0, 180.0);
    assert!((d - 20_015_087.0).abs() < 60_000.0, "got {d}");
}

#[test]
fn haversine_pole_to_pole() {
    let d = haversine(90.0, 0.0, -90.0, 0.0);
    assert!((d - 20_015_087.0).abs() < 60_000.0, "got {d}");
}

#[test]
fn matrix_haversine_skips_unresolved() {
    let locs = vec![
        loc("A", 47.0, -117.0),
        unresolved("B"),
        loc("C", 47.1, -117.1),
    ];
    let m = build_distance_matrix(&locs, Backend::Haversine, None, None).unwrap();
    assert_eq!(m.len(), 2);
    assert!(m.iter().all(|r| r.len() == 2));
    assert_eq!(m[0][0], 0.0);
    assert!(m[0][1] > 0.0);
    assert_eq!(m[0][1], m[1][0]);
}

#[test]
fn matrix_no_resolved_locations_is_error() {
    let locs = vec![unresolved("A"), unresolved("B")];
    assert!(build_distance_matrix(&locs, Backend::Haversine, None, None).is_err());
    assert!(build_distance_matrix(&[], Backend::Haversine, None, None).is_err());
}

#[test]
fn matrix_google_backend_requires_key() {
    let locs = vec![loc("A", 47.0, -117.0)];
    assert!(build_distance_matrix(&locs, Backend::Google, None, None).is_err());
    assert!(build_distance_matrix(&locs, Backend::Google, None, Some("")).is_err());
}
