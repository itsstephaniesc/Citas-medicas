const doctorsBySpecialty = {
  "Medicina general": ["Dra. Ana Vargas", "Dr. Carlos Pérez"],
  Cardiología: ["Dr. Luis Mora", "Dra. Sofía Rojas"],
  Dermatología: ["Dra. Elena Castro", "Dr. Pablo Solís"],
  Pediatría: ["Dra. Laura Jiménez", "Dr. Andrés Vega"],
};
const specialty = document.getElementById("specialty");
const doctor = document.getElementById("doctor");
const dateInput = document.getElementById("date");
const timeInput = document.getElementById("time");
const message = document.getElementById("message");
const summary = document.getElementById("summary");
// Demo: las citas solo se conservan mientras esta página permanezca abierta.
const appointments = [];

function localDateString(date = new Date()) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}
dateInput.min = localDateString();

specialty.addEventListener("change", () => {
  doctor.innerHTML = '<option value="">Seleccione médico...</option>';
  (doctorsBySpecialty[specialty.value] || []).forEach((name) => {
    const option = document.createElement("option");
    option.value = name;
    option.textContent = name;
    doctor.appendChild(option);
  });
});

function showMessage(text, type) {
  message.textContent = text;
  message.className = `message ${type}`;
}

document.getElementById("bookingForm").addEventListener("submit", (event) => {
  event.preventDefault();
  const patient = document.getElementById("patient").value.trim();
  const chosenSpecialty = specialty.value;
  const chosenDoctor = doctor.value;
  const date = dateInput.value;
  const time = timeInput.value;

  // Admite letras Unicode (incluidos acentos) y espacios entre palabras.
  if (!patient)
    return showMessage(
      "Error: el nombre del paciente es obligatorio.",
      "error",
    );
  if (!/^[\p{L}\p{M} ]+$/u.test(patient))
    return showMessage(
      "Error: el nombre solo puede contener letras y espacios.",
      "error",
    );
  if (!chosenSpecialty || !chosenDoctor)
    return showMessage(
      "Error: seleccione una especialidad y un médico.",
      "error",
    );
  if (!date) return showMessage("Error: seleccione una fecha.", "error");
  if (date < localDateString())
    return showMessage(
      "Error: no se permiten citas para fechas pasadas.",
      "error",
    );
  if (!time) return showMessage("Error: seleccione una hora.", "error");

  const [hours, minutes] = time.split(":").map(Number);
  const minuteOfDay = hours * 60 + minutes;
  if (minuteOfDay < 8 * 60 || minuteOfDay > 17 * 60)
    return showMessage(
      "Error: el horario permitido es de 8:00 a. m. a 5:00 p. m.",
      "error",
    );

  // Evita elegir una hora que ya pasó si la cita es hoy.
  if (date === localDateString()) {
    const now = new Date();
    if (minuteOfDay <= now.getHours() * 60 + now.getMinutes())
      return showMessage(
        "Error: seleccione una hora futura para hoy.",
        "error",
      );
  }

  const duplicate = appointments.some(
    (a) => a.doctor === chosenDoctor && a.date === date && a.time === time,
  );
  if (duplicate)
    return showMessage(
      "Error: este médico ya tiene una cita en esa fecha y hora.",
      "error",
    );

  const appointment = {
    patient,
    specialty: chosenSpecialty,
    doctor: chosenDoctor,
    date,
    time,
  };
  appointments.push(appointment);
  showMessage("¡Cita reservada correctamente!", "success");
  summary.innerHTML = "";
  const title = document.createElement("h3");
  title.textContent = "Cita confirmada";
  summary.appendChild(title);
  [
    `Paciente: ${patient}`,
    `Especialidad: ${chosenSpecialty}`,
    `Médico: ${chosenDoctor}`,
    `Fecha: ${date}`,
    `Hora: ${time}`,
  ].forEach((line) => {
    const p = document.createElement("p");
    p.textContent = line;
    summary.appendChild(p);
  });
  document.getElementById("bookingForm").reset();
  doctor.innerHTML =
    '<option value="">Seleccione especialidad primero...</option>';
  dateInput.min = localDateString();
});
