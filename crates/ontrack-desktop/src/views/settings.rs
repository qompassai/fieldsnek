#[cfg(not(target_arch = "wasm32"))]
use std::fs;
#[cfg(not(target_arch = "wasm32"))]
use std::path::PathBuf;

use eframe::egui;
use ontrack_core::solver::SolverBackend;

use crate::app::OnTrackApp;

pub fn ui(app: &mut OnTrackApp, ui: &mut egui::Ui) {
    ui.heading("Settings");
    ui.add_space(8.0);

    egui::Grid::new("settings_grid")
        .num_columns(2)
        .spacing([8.0, 6.0])
        .show(ui, |ui| {
            ui.label("Google Maps API key:");
            ui.add(
                egui::TextEdit::singleline(&mut app.settings.google_maps_api_key)
                    .desired_width(420.0)
                    .password(true),
            );
            ui.end_row();

            ui.label("OSRM Base URL:");
            ui.add(
                egui::TextEdit::singleline(&mut app.settings.osrm_base_url).desired_width(420.0),
            );
            ui.end_row();

            ui.label("ArcGIS Item ID:");
            ui.add(
                egui::TextEdit::singleline(&mut app.settings.arcgis_item_id).desired_width(420.0),
            );
            ui.end_row();

            ui.label("Whisper model:");
            ui.add(
                egui::TextEdit::singleline(&mut app.settings.whisper_model).desired_width(160.0),
            );
            ui.end_row();
        });

    ui.add_space(12.0);
    ui.heading("Route solver");
    ui.add_space(8.0);

    egui::Grid::new("solver_grid")
        .num_columns(2)
        .spacing([8.0, 6.0])
        .show(ui, |ui| {
            ui.label("Solver backend:");
            egui::ComboBox::from_id_salt("solver_backend_combo")
                .selected_text(match app.solver_backend {
                    SolverBackend::NearestNeighbor => "Nearest neighbor",
                    SolverBackend::NearestNeighborTwoOpt => "Nearest neighbor + 2-opt",
                })
                .show_ui(ui, |ui| {
                    ui.selectable_value(
                        &mut app.solver_backend,
                        SolverBackend::NearestNeighbor,
                        "Nearest neighbor",
                    );
                    ui.selectable_value(
                        &mut app.solver_backend,
                        SolverBackend::NearestNeighborTwoOpt,
                        "Nearest neighbor + 2-opt",
                    );
                });
            ui.end_row();

            ui.label("2-opt passes:");
            ui.add(egui::DragValue::new(&mut app.two_opt_passes).range(0..=500));
            ui.end_row();
        });

    ui.add_space(4.0);
    ui.checkbox(&mut app.return_to_start, "Return to start (closed loop)");
    ui.label("Unchecked: the route ends at the last stop instead of returning to the depot.");

    ui.add_space(8.0);
    #[cfg(not(target_arch = "wasm32"))]
    if ui.button("💾  Save to .env").clicked() {
        if let Err(e) = save_env(&app.settings) {
            let mut w = app.worker.lock().unwrap();
            w.error = Some(format!("save: {e}"));
        }
    }
    // Browser build: there is no filesystem to persist to — settings
    // typed here apply for this tab session only.
    #[cfg(target_arch = "wasm32")]
    ui.label("Settings apply to this browser session only (the web build has no .env file).");
    ui.add_space(8.0);
    #[cfg(not(target_arch = "wasm32"))]
    ui.label(
        "Note: keys are stored only in your local .env file — never transmitted to TDS servers.",
    );
    #[cfg(target_arch = "wasm32")]
    ui.label("Note: keys stay in this tab's memory — never transmitted to TDS servers.");
}

#[cfg(not(target_arch = "wasm32"))]
fn save_env(s: &ontrack_core::config::Settings) -> anyhow::Result<()> {
    let path = PathBuf::from(".env");
    let contents = format!(
        "GOOGLE_MAPS_API_KEY=\"{}\"\nOSRM_BASE_URL=\"{}\"\nARCGIS_ITEM_ID=\"{}\"\nONTRACK_WHISPER_MODEL=\"{}\"\n",
        s.google_maps_api_key, s.osrm_base_url, s.arcgis_item_id, s.whisper_model,
    );
    fs::write(path, contents)?;
    Ok(())
}
