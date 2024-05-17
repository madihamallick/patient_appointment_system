import React, { useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";

const PaymentDone = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  useEffect(() => {
    const markPayment = async () => {
      try {
        const response = await fetch(
          `${process.env.REACT_APP_FAST_API}/appointments/${id}/payment`,
          {
            method: "PATCH",
            headers: {
              "Content-Type": "application/json",
            },
          }
        );

        if (!response.ok) {
          throw new Error("Failed to mark payment");
        }

        console.log("Payment marked successfully");
      } catch (error) {
        console.error(error);
      }
    };
    markPayment(localStorage.getItem("appointment_id"));
  }, [id]);
  return (
    <div className="text-center flex justify-center items-center flex-col pt-28">
        <p className="text-3xl font-bold my-10">Payment Done</p>
      <button
        className="bg-red-500 hover:bg-red-600 transition-all text-white py-4 px-6 rounded inline-block text-md font-semibold relative before:absolute before:bg-gradient-to-tr before:from-yellow-600 before:via-transparent before:to-green-700 before:inset-0 before:scale-110 before:rounded before:blur-md before:-z-10"
        onClick={() => navigate("/allpatients")}
      >
        Go To Patients
      </button>
    </div>
  );
};

export default PaymentDone;
