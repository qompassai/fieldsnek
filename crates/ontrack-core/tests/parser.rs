use ontrack_core::{parse_addresses, parse_addresses_from_bytes};
use std::io::Write;

#[test]
fn parses_csv_with_header() {
    let tmp = std::env::temp_dir().join("ontrack-rs-parser.csv");
    let mut f = std::fs::File::create(&tmp).unwrap();
    writeln!(f, "address,note").unwrap();
    writeln!(f, "123 Main St Spokane WA,foo").unwrap();
    writeln!(f, "456 Elm St,").unwrap();
    writeln!(f, ",empty").unwrap();
    drop(f);

    let addrs = parse_addresses(&tmp).unwrap();
    assert_eq!(addrs.len(), 2);
    assert_eq!(addrs[0], "123 Main St Spokane WA");
    assert_eq!(addrs[1], "456 Elm St");
    std::fs::remove_file(&tmp).ok();
}

#[test]
fn missing_address_column_is_error() {
    let tmp = std::env::temp_dir().join("ontrack-rs-parser-bad.csv");
    let mut f = std::fs::File::create(&tmp).unwrap();
    writeln!(f, "street,city").unwrap();
    writeln!(f, "123 Main,Spokane").unwrap();
    drop(f);
    assert!(parse_addresses(&tmp).is_err());
    std::fs::remove_file(&tmp).ok();
}

#[test]
fn parses_csv_from_bytes() {
    let bytes = b"address,note\n123 Main St Spokane WA,foo\n456 Elm St,\n,empty\n";
    let addrs = parse_addresses_from_bytes("stops.csv", bytes).unwrap();
    assert_eq!(
        addrs,
        vec![
            "123 Main St Spokane WA".to_string(),
            "456 Elm St".to_string()
        ]
    );
}

#[test]
fn bytes_missing_address_column_is_error() {
    let bytes = b"street,city\n123 Main,Spokane\n";
    assert!(parse_addresses_from_bytes("stops.csv", bytes).is_err());
}

#[test]
fn bytes_unsupported_extension_is_error() {
    assert!(parse_addresses_from_bytes("stops.txt", b"address\n123 Main\n").is_err());
    assert!(parse_addresses_from_bytes("stops", b"address\n123 Main\n").is_err());
}

#[test]
fn bytes_empty_input_is_error() {
    assert!(parse_addresses_from_bytes("stops.csv", b"").is_err());
}
