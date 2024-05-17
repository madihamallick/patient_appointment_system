import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

const Patient = () => {
  const { id } = useParams();
  const [patientData, setPatientData] = useState(null);

  useEffect(() => {
    fetch(`${process.env.REACT_APP_FAST_API}/patients/${id}/details`)
      .then((response) => response.json())
      .then((data) => {
        setPatientData(data);
      })
      .catch((error) => console.error("Error fetching patient data:", error));
  }, [id]);

  if (!patientData) {
    return <div>Loading...</div>;
  }

  const markAppointmentComplete = async (appointmentId) => {
    try {
      const response = await fetch(`${process.env.REACT_APP_FAST_API}/appointments/${appointmentId}/complete`, {
        method: "PATCH",
        headers: {
          Accept: "application/json",
        },
      });

      if (!response.ok) {
        throw new Error("Failed to mark appointment as complete");
      }

      const responseData = await response.json();
      alert("Appointment marked as complete");
      console.log(responseData);
      window.location.reload();
    } catch (error) {
      console.error("Error marking appointment as complete:", error);
    }
  };

  return (
    <div className="max-w-7xl mx-auto p-4">
      <h2 className="text-3xl font-extrabold text-center pt-16">
        Patient Details
      </h2>
      <div className="p-6 mb-6">
        <h2 className="text-xl font-bold mb-4">{patientData.name}'s Details</h2>
        <p>
          <strong>Email:</strong> {patientData.email}
        </p>
        <p>
          <strong>Mobile:</strong> {patientData.mobile}
        </p>
        <p>
          <strong>Username:</strong> {patientData.username}
        </p>
        <p>
          <strong>Problem:</strong> {patientData.problem}
        </p>
        <p>
          <strong>User ID:</strong> {patientData.user_id}
        </p>
        <p>
          <strong>Created At:</strong>
          {new Date(patientData.created_at).toLocaleString()}
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-4 mt-6">
        {patientData.appointments.map((appointment) => (
          <div
            key={appointment.id}
            className="border shadow-lg rounded-lg p-6 mb-4"
          >
            <h3 className="text-lg font-semibold mb-2">{appointment.note}</h3>
            <p>
              <strong>Date:</strong>{" "}
              {new Date(appointment.appointment_date).toLocaleDateString()}
            </p>
            <p>
              <strong>Price:</strong> ₹1000
            </p>
            <p>
              <strong>Payment Status:</strong>{" "}
              {appointment.payment_status === "0" ? "Not Paid" : "Paid"}
            </p>
            <p>
              <strong>Appointment Status:</strong>{" "}
              {appointment.appointment_status || "No Status"}
            </p>
            <p>
              <strong>Payment Link:</strong>{" "}
              <a
                href={appointment.payment_link}
                target="_blank"
                rel="noopener noreferrer"
              >
                View Payment
              </a>
            </p>
            <div className="flex items-start">
              <button
                className="flex mt-6 flex-row items-center justify-center w-full px-4 py-4 mb-4 text-sm font-bold bg-green-300 leading-6 capitalize duration-100 transform rounded-sm shadow cursor-pointer focus:ring-4 focus:ring-green-500 focus:ring-opacity-50 focus:outline-none sm:mb-0 sm:w-auto sm:mr-4 md:pl-8 md:pr-6 xl:pl-12 xl:pr-10   hover:shadow-lg hover:-translate-y-1"
                onClick={() => markAppointmentComplete(appointment.id)}
              >
                Mark Complete
              </button>
              <button
                className="flex h-14 items-center justify-center w-full px-4 py-4 mt-6 text-sm font-bold leading-6 capitalize duration-100 transform border-2 rounded-sm cursor-pointer border-green-300 focus:ring-4 focus:ring-green-500 focus:ring-opacity-50 focus:outline-none sm:w-auto sm:px-6 border-text  hover:shadow-lg hover:-translate-y-1"
                onClick={() => window.open(appointment.payment_link, "_blank")}
              >
                Make Payment
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Patient;
