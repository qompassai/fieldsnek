use ontrack_core::geocoder::Location;
use ontrack_core::matrix::haversine;
use ontrack_core::solver::{solve_open_tsp, solve_tsp, SolverConfig};

fn loc(name: &str, lat: f64, lng: f64) -> Location {
    Location {
        address: name.into(),
        lat: Some(lat),
        lng: Some(lng),
    }
}

#[test]
fn solves_realistic_spokane_loop() {
    let pts = vec![
        loc("Downtown Spokane", 47.6588, -117.4260),
        loc("Spokane Valley Mall", 47.6750, -117.2364),
        loc("Liberty Lake", 47.6717, -117.0892),
        loc("Cheney WA", 47.4874, -117.5758),
        loc("Mead WA", 47.7705, -117.3540),
    ];
    let n = pts.len();
    let mut matrix = vec![vec![0.0_f64; n]; n];
    for i in 0..n {
        for j in 0..n {
            matrix[i][j] = haversine(
                pts[i].lat.unwrap(),
                pts[i].lng.unwrap(),
                pts[j].lat.unwrap(),
                pts[j].lng.unwrap(),
            );
        }
    }
    let r = solve_tsp(&pts, &matrix, SolverConfig::default()).unwrap();
    assert_eq!(r.ordered_indices.len(), n);
    assert_eq!(r.ordered_indices[0], 0);
}

#[test]
fn open_tsp_strips_dummy_node() {
    let pts = vec![loc("A", 0.0, 0.0), loc("B", 0.0, 1.0), loc("C", 1.0, 1.0)];
    let matrix = vec![
        vec![0.0, 1.0, 2.0],
        vec![1.0, 0.0, 1.0],
        vec![2.0, 1.0, 0.0],
    ];
    let r = solve_open_tsp(&pts, &matrix, SolverConfig::default()).unwrap();
    assert_eq!(r.ordered_addresses.len(), 3);
    assert!(!r.ordered_addresses.iter().any(|a| a == "__end__"));
}

#[test]
fn empty_locations_is_error() {
    let matrix: Vec<Vec<f64>> = vec![];
    assert!(solve_tsp(&[], &matrix, SolverConfig::default()).is_err());
}

#[test]
fn nonsquare_matrix_is_error() {
    let pts = vec![loc("A", 0.0, 0.0), loc("B", 0.0, 1.0)];
    let matrix = vec![vec![0.0, 1.0], vec![1.0]];
    assert!(solve_tsp(&pts, &matrix, SolverConfig::default()).is_err());
}

#[test]
fn depot_out_of_range_is_error() {
    let pts = vec![loc("A", 0.0, 0.0), loc("B", 0.0, 1.0)];
    let matrix = vec![vec![0.0, 1.0], vec![1.0, 0.0]];
    let cfg = SolverConfig {
        depot_index: 5,
        ..Default::default()
    };
    assert!(solve_tsp(&pts, &matrix, cfg).is_err());
}

#[test]
fn single_location_route() {
    let pts = vec![loc("A", 0.0, 0.0)];
    let matrix = vec![vec![0.0]];
    let r = solve_tsp(&pts, &matrix, SolverConfig::default()).unwrap();
    assert_eq!(r.ordered_indices, vec![0]);
    assert_eq!(r.total_duration_seconds, 0.0);
}

#[test]
fn open_route_skips_the_return_leg() {
    let pts = vec![loc("A", 0.0, 0.0), loc("B", 0.0, 1.0), loc("C", 1.0, 1.0)];
    let matrix = vec![
        vec![0.0, 1.0, 2.0],
        vec![1.0, 0.0, 1.0],
        vec![2.0, 1.0, 0.0],
    ];
    let closed = solve_tsp(&pts, &matrix, SolverConfig::default()).unwrap();
    let open = solve_open_tsp(&pts, &matrix, SolverConfig::default()).unwrap();
    assert_eq!(open.ordered_indices.len(), 3);
    assert!(open.total_duration_seconds < closed.total_duration_seconds);
}
