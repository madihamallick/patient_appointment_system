import React, { useState } from "react";
import { IoLogOutOutline } from "react-icons/io5";
import { useNavigate, useParams } from "react-router-dom";

const AddAppointment = () => {
  const navigate = useNavigate();
  const params = useParams();

  const [formData, setFormData] = useState({
    date: "",
    note: "",
  });

  const handleSubmit = async (e) => {
    e.preventDefault();

    const appointmentDateObj = new Date(formData.date);

    const payload = {
        appointment_date: Math.floor(appointmentDateObj.getTime() / 1000),
        price: 0,
        note: formData.note,
        payment_status: false,
        user_id: localStorage.getItem("user_id"),
        patient_id: params.id,
    };

    try {
      const response = await fetch(`${process.env.REACT_APP_FAST_API}/appointments/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error("Failed to register user");
      }

      navigate("/allpatients");
    } catch (error) {
      console.error(error.message);
    }
  };
  return (
    <div>
      <div
        className="flex justify-end px-5 pt-2 cursor-pointer"
        onClick={() => {
          localStorage.removeItem("user");
          localStorage.removeItem("user_id");
          navigate("/signin");
        }}
      >
        <span className="pt-1 pr-3">{localStorage.getItem("user")}</span>
        <IoLogOutOutline className="text-3xl " />
      </div>
      <h1 class="text-2xl xl:text-3xl font-extrabold text-center  md:pt-28 pt-10">
        Add Appointment
      </h1>

      <div class="w-full flex-1 mt-8">
        <div class="mx-auto max-w-md">
          <form onSubmit={handleSubmit}>
            <input
              class="w-full px-8 py-4 my-3 rounded-lg font-medium bg-gray-100 border border-gray-200 placeholder-gray-500 text-sm focus:outline-none focus:border-gray-400 focus:bg-white"
              type="datetime-local"
              placeholder="Appointment Date"
              value={formData.date}
              onChange={(e) =>
                setFormData({ ...formData, date: e.target.value })
              }
            />
            <input
              class="w-full px-8 py-4 my-3 rounded-lg font-medium bg-gray-100 border border-gray-200 placeholder-gray-500 text-sm focus:outline-none focus:border-gray-400 focus:bg-white"
              type="note"
              placeholder="note"
              value={formData.note}
              onChange={(e) =>
                setFormData({ ...formData, note: e.target.value })
              }
            />
            <button
              type="submit"
              class="mt-5 tracking-wide font-semibold bg-blue-500 text-gray-100 w-full py-4 rounded-lg hover:bg-blue-700 transition-all duration-300 ease-in-out flex items-center justify-center focus:shadow-outline focus:outline-none"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke-width="1.5"
                stroke="currentColor"
                class="w-6 h-6"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="M17.25 8.25 21 12m0 0-3.75 3.75M21 12H3"
                />
              </svg>

              <span class="ml-3">Add Appointment</span>
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default AddAppointment;
