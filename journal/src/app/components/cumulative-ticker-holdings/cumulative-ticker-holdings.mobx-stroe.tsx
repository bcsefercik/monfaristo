import mApi from "@/app/utils/m-api";
import { makeAutoObservable } from "mobx";

export interface UserProps {
  has_instructor_intent: boolean;
}
export default class CumulativeTickerHoldingsStore {
  books: string;
  constructor() {
    this.books = "asdf";
    makeAutoObservable(this);
  }

  async fetcthData() {
    mApi.get("/currencies").then((response) => {
      console.log(response);
    });
  }
}
